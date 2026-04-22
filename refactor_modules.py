import os
import glob
import shutil
import re

DOMAINS = {
    'ethics': [
        'absolute_evil', 'buffer', 'deontic_gate', 'ethical_mixture_likelihood', 
        'ethical_poles', 'ethical_reflection', 'pole_linear', 'ml_ethics_tuner',
        'weights_', 'weighted_ethics_scorer', 'weight_authority', 'pad_archetypes', 'weakness_pole'
    ],
    'cognition': [
        'bayesian_engine', 'bayesian_mixture_averaging', 'charm_engine', 
        'consequence_projection', 'context_distillation', 'epistemic_dissonance',
        'epistemic_humility', 'feedback_calibration_ledger', 'feedback_mixture_posterior',
        'feedback_mixture_updater', 'generative_candidates', 'hierarchical_updater',
        'metacognition', 'metaplan_registry', 'motivation_engine', 'premise_validation',
        'salience_map', 'strategy_engine', 'subjective_time', 'temporal_horizon_prior',
        'temporal_planning', 'turn_prefetcher', 'variability', 'working_memory', 'sigmoid_will'
    ],
    'memory': [
        'forgiveness', 'immortality', 'memory_hygiene', 'migratory_identity',
        'narrative', 'narrative_identity', 'narrative_types', 'persistent_threat_tracker',
        'session_checkpoint', 'psi_sleep', 'reparation_vault', 'semantic_anchor_store',
        'semantic_embedding_client', 'precedent_rag'
    ],
    'social': [
        'gray_zone_diplomacy', 'uchi_soto', 'swarm_negotiator', 'swarm_oracle',
        'swarm_peer_stub', 'user_model'
    ],
    'governance': [
        'audit_chain_log', 'conduct_guide_export', 'dao_orchestrator', 'evidence_safe',
        'existential_serialization', 'external_audit_framework', 'hub_audit',
        'identity_integrity', 'identity_reflection', 'lan_governance_conflict_taxonomy',
        'lan_governance_coordinator', 'lan_governance_envelope', 'lan_governance_event_merge',
        'lan_governance_merge_context', 'lan_governance_replay_sidecar', 'mock_dao',
        'mock_dao_audit_replay', 'moral_hub', 'multi_realm_governance', 'nomad_identity'
    ],
    'somatic': [
        'affect_projection_relay', 'affective_homeostasis', 'comfort_monitor',
        'hardware_abstraction', 'somatic_adapter', 'somatic_markers', 'somatic_signal_mapper',
        'sympathetic', 'vitality', 'soft_robotics'
    ],
    'perception': [
        'audio_adapter', 'audio_ouroboros', 'audio_signal_mapper', 'input_trust',
        'multimodal_trust', 'nomad_bridge', 'nomad_chat_adapter', 'nomad_discovery',
        'nomad_session_sync', 'perception_async_handler', 'perception_backend_policy',
        'perception_circuit', 'perception_confidence', 'perception_cross_check',
        'perception_dual_vote', 'perception_schema', 'perceptual_abstraction',
        'sensor_baseline_calibrator', 'sensor_calibration', 'sensor_contracts',
        'vision_adapter', 'vision_capture', 'vision_inference', 'vision_multiprocess',
        'vision_signal_mapper', 'zeroconf_discovery'
    ],
    'safety': [
        'env_coherence_check', 'guardian_mode', 'guardian_routines', 'help_request_protocol',
        'judicial_escalation', 'light_risk_classifier', 'local_sovereignty', 'locus',
        'privacy_shield', 'reality_verification', 'safety_interlock', 'semantic_chat_gate',
        'transparency_s10'
    ]
}

# Add any unmapped files to 'core' or existing folders
# LLM stuff
DOMAINS['cognition'].extend(['llm_backends', 'llm_cancel_burst', 'llm_http_cancel', 'llm_layer', 'llm_touchpoint_policies', 'llm_verbal_backend_policy', 'rlhf_reward_model'])
DOMAINS['perception'].extend(['action_narrator', 'operator_hud', 'orchestration_trace'])
DOMAINS['governance'].extend(['secure_boot'])
DOMAINS['cognition'].extend(['skill_learning_registry', 'basal_ganglia'])
DOMAINS['safety'].extend(['kernel_event_bus', 'async_task_canceller'])

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src/modules'))
REPO_ROOT = os.path.abspath(os.path.dirname(__file__))

def get_target_domain(filename):
    name = filename.replace('.py', '')
    for domain, patterns in DOMAINS.items():
        for pat in patterns:
            if name == pat or (pat.endswith('_') and name.startswith(pat)):
                return domain
    return None

def run():
    # Create directories
    for domain in DOMAINS.keys():
        dpath = os.path.join(BASE_DIR, domain)
        if not os.path.exists(dpath):
            os.makedirs(dpath)
            # Add __init__.py
            with open(os.path.join(dpath, '__init__.py'), 'w') as f:
                f.write('')
                
    file_map = {} # old_module_name -> (domain, new_module_name)
    
    # Move files
    for f in os.listdir(BASE_DIR):
        if not f.endswith('.py') or f == '__init__.py':
            continue
        filepath = os.path.join(BASE_DIR, f)
        if not os.path.isfile(filepath):
            continue
            
        domain = get_target_domain(f)
        if domain:
            target_path = os.path.join(BASE_DIR, domain, f)
            print(f"Moving {f} -> {domain}/{f}")
            shutil.move(filepath, target_path)
            mod_name = f.replace('.py', '')
            file_map[mod_name] = domain
        else:
            print(f"Warning: No domain found for {f}")

    # Now we need to update imports across the repo
    # Find all .py files
    py_files = []
    for root, dirs, files in os.walk(REPO_ROOT):
        if '.git' in root or '__pycache__' in root or '.venv' in root:
            continue
        for f in files:
            if f.endswith('.py'):
                py_files.append(os.path.join(root, f))
                
    import_pattern = re.compile(r'(from|import)\s+src\.modules\.([a-zA-Z0-9_]+)')
    
    for pf in py_files:
        with open(pf, 'r', encoding='utf-8') as f:
            content = f.read()
            
        new_content = content
        
        def replacer(match):
            keyword = match.group(1)
            mod = match.group(2)
            if mod in file_map:
                domain = file_map[mod]
                return f"{keyword} src.modules.{domain}.{mod}"
            return match.group(0)
            
        new_content = import_pattern.sub(replacer, new_content)
        
        if new_content != content:
            with open(pf, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated imports in {pf}")

if __name__ == '__main__':
    run()
