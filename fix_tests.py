import os

files = ['tests/test_nomad_vision_consumer.py', 'tests/test_vision_continuous_daemon.py', 'tests/test_rlhf_reward_model.py']
for f in files:
    if os.path.exists(f):
        with open(f, 'r') as fp: content = fp.read()
        if 'pytest.importorskip("torch")' not in content:
            with open(f, 'w') as fp: fp.write('import pytest\npytest.importorskip("torch")\n' + content)

files2 = ['tests/test_semantic_anchor_store.py', 'tests/test_semantic_chat_gate.py', 'tests/test_semantic_robustness.py']
for f in files2:
    if os.path.exists(f):
        with open(f, 'r') as fp: content = fp.read()
        if 'pytest.importorskip("chromadb")' not in content:
            with open(f, 'w') as fp: fp.write('import pytest\npytest.importorskip("chromadb")\n' + content)
print('Done!')
