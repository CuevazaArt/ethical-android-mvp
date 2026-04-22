import logging
import multiprocessing as mp
import time
from multiprocessing import shared_memory

import numpy as np

from .vision_adapter import VisionInference, from_env_vision_adapter

_log = logging.getLogger(__name__)

# Phase 9: B.4.2 Dedicated Vision Process Wrapper
# This ensures heavy ONNX/Torch inference never blocks the main Asyncio Event Loop.


def vision_worker(
    input_queue: mp.Queue,
    output_queue: mp.Queue,
    stop_event: mp.Event,
    shm_name: str,
    shm_shape: tuple,
    shm_dtype: np.dtype,
):
    """Isolated process worker for vision inference using SharedMemory."""
    # Initialize adapter inside the process
    adapter = from_env_vision_adapter()
    adapter.load_model()

    _log.info("Vision Worker Process started (Zero-Copy SharedMemory mode).")

    # Attach to shared memory
    shm = shared_memory.SharedMemory(name=shm_name)
    shm_array = np.ndarray(shm_shape, dtype=shm_dtype, buffer=shm.buf)

    while not stop_event.is_set():
        try:
            # Wait for signal that a new frame is ready in SHM
            # We use the queue as a signaling mechanism for synchronization
            msg = input_queue.get(timeout=0.1)
            if msg != "NEW_FRAME":
                continue

            # Run inference on the shared buffer (no copying!)
            # We copy once locally if the adapter needs to modify the array,
            # but usually they are read-only.
            result = adapter.infer(shm_array)

            # Put result in output queue
            while not output_queue.empty():
                try:
                    output_queue.get_nowait()
                except Exception:
                    break
            output_queue.put(result)

        except mp.queues.Empty:
            continue
        except Exception as e:
            _log.error("Vision Worker Error: %s", e)
            time.sleep(1)

    shm.close()


class MultiprocessVisionInference:
    """
    Manager for the dedicated Vision Process with SharedMemory support.
    """

    def __init__(self, frame_shape=(480, 640, 3), dtype=np.uint8):
        self._frame_shape = frame_shape
        self._dtype = dtype

        # Create Shared Memory block (size in bytes)
        size = np.prod(frame_shape) * np.dtype(dtype).itemsize
        self._shm = shared_memory.SharedMemory(create=True, size=size)
        self._shm_array = np.ndarray(frame_shape, dtype=dtype, buffer=self._shm.buf)

        self._input_q = mp.Queue(maxsize=1)
        self._output_q = mp.Queue(maxsize=1)
        self._stop_event = mp.Event()
        self._process: mp.Process | None = None
        self.latest_result: VisionInference | None = None

    def start(self):
        if self._process:
            return
        self._stop_event.clear()
        self._process = mp.Process(
            target=vision_worker,
            args=(
                self._input_q,
                self._output_q,
                self._stop_event,
                self._shm.name,
                self._frame_shape,
                self._dtype,
            ),
            daemon=True,
        )
        self._process.start()

    def stop(self):
        if not self._process:
            return
        self._stop_event.set()
        self._process.join(timeout=2)
        if self._process.is_alive():
            self._process.terminate()
        self._shm.close()
        self._shm.unlink()
        self._process = None

    def submit_frame(self, frame: np.ndarray):
        """Zero-copy submission: copies frame into SHM and signals worker."""
        if frame.shape != self._frame_shape:
            # Resize if necessary to fit the fixed SHM buffer
            import cv2

            frame = cv2.resize(frame, (self._frame_shape[1], self._frame_shape[0]))

        # Copy into the shared buffer (one copy only, instead of pickle/pipe overhead)
        np.copyto(self._shm_array, frame)

        # Signal the worker via queue
        if self._input_q.full():
            try:
                self._input_q.get_nowait()
            except Exception:
                pass
        self._input_q.put("NEW_FRAME")

    def poll_result(self) -> VisionInference | None:
        """Non-blocking retrieval of the latest inference result."""
        try:
            res = self._output_q.get_nowait()
            self.latest_result = res
            return res
        except Exception:
            return self.latest_result
