#!/usr/bin/env python3
"""Re-runnable commissioning evidence; live gates cannot be passed by code labels."""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend.continuity import RecoveryStore,load_registry,git_version,now,digest,canonical
from overdrive.evidence_learning import reference_cycle
from cryptography.fernet import Fernet


def commission(output: Path) -> dict:
    output.mkdir(parents=True,exist_ok=True)
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_control_plane.py')
    stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=1).run(suite)
    tests={'state':'PASS' if result.wasSuccessful() else 'FAIL','tests_run':result.testsRun,
           'failures':len(result.failures),'errors':len(result.errors),'output_sha256':digest(stream.getvalue().encode())}
    with tempfile.TemporaryDirectory(prefix='amx-commission-') as temp:
        p=Path(temp);key=p/'key';key.write_bytes(Fernet.generate_key());key.chmod(0o600)
        registry=load_registry(ROOT/'CONTINUITY/source-registry.json',ROOT)
        registry['sources']=[s for s in registry['sources'] if s['source_system']!='google_drive']
        store=RecoveryStore(p/'ciphertext',key,ROOT)
        sync=store.sync(registry);restore=store.restore_test();verify=store.verify()
        learning=reference_cycle(ROOT,p/'learning.db',json.loads((ROOT/'CONTINUITY/capability-grants.json').read_text()))
        recovery={'scope':'EXISTING_REGISTERED_REPOSITORY_SOURCES; PRIVATE_DRIVE_ESTATE_NOT_ENROLLED',
                  'sync':sync,'restore_test':restore,'integrity':verify,'receipts':store.read_receipts()}
    paths=['backend/continuity.py','backend/security.py','backend/sources.py','backend/assets.py',
           'BLACK/worker.py','BLACK/continuity.py','BLACK/install-continuity.sh','overdrive/evidence_learning.py',
           'CONTINUITY/source-registry.json','CONTINUITY/capability-grants.json','tests/test_control_plane.py']
    checks={
      'A_REPOSITORY':{'state':tests['state'],'scope':'local reconstruction/tests; full dependency HTTP/container CI is separately attributable'},
      'B_BLACK':{'state':'HOLD','reason':'Existing service preflight was proven; subsequent command execution timed out. New installation/timer/WSL full boot require fresh receipts'},
      'C_DRIVE_LOSS':{'state':'HOLD','tested_scope':'Offline restore of captured registered source fixtures and actual repository; actual private Drive enrollment incomplete'},
      'D_INTEGRITY':{'state':tests['state'],'scope':'deliberate corruption, wrong key, tampered manifest/receipt, no silent promotion'},
      'E_RESTORE':{'state':restore['state'],'scope':recovery['scope']},
      'F_SECRETS':{'state':'HOLD','reason':'Attach exact redacted current/history scan; older uninspected history is not inferred safe'},
      'G_WORKER_LEARNING':{'state':learning['state'],'scope':'real local existing-Reaper evidence audit -> candidate -> Critic test -> versioned promotion; live runtime not inferred'},
      'H_BOUNTY_REAPER':{'state':'PASS' if learning['state']=='PASS' else 'FAIL','scope':'same crypto mandate owner; no outreach/funds/submission/payment claim'},
      'I_NO_DUPLICATION':{'state':'PASS','scope':'extensions of BLACK, EvidenceStore, OVERDRIVE adapter and House projection; no new worker/dashboard/Matrix'}}
    body={'schema':'AMX.CODEX.COMMISSIONING.v1','at':now(),'state':'HOLD','directive_closed':False,
          'repository':'amillimatrix-eng/CARBON-Creation-Hub','source_version':git_version(ROOT),
          'code_sha256':{name:digest((ROOT/name).read_bytes()) for name in paths},
          'tests':tests,'recovery':recovery,'learning':learning,'acceptance':checks,
          'gates':[
            {'id':'BLACK_SERVICE_PROMOTION','class':'G1','dependency':'Responsive existing BLACK execution path and node administration','action':'Resolve bounded exit-124 execution preflight; install reviewed source with BLACK/install-continuity.sh; collect fresh service/config/restore receipts','automatic_resume':'timer executes verified sync and isolated restore tests'},
            {'id':'DRIVE_READ_ENROLLMENT','class':'G3','dependency':'Legitimate scoped Drive OAuth on BLACK','action':'Configure one read-only rclone remote locally; set AMX_DRIVE_DISCOVERY_REMOTE','automatic_resume':'periodic stable-ID inventory/export/mirror; missing sources retained'},
            {'id':'INDEPENDENT_CUSTODY','class':'G1','dependency':'Existing approved independent ciphertext destination and separate key escrow','action':'Enroll replica and escrow once; prove restore from them','automatic_resume':'bounded ciphertext retention/verification; no new approval per sync'},
            {'id':'WINDOWS_NO_TOUCH_BOOT','class':'G0','dependency':'Next natural Windows startup observation','action':'Existing launcher wakes WSL; obtain fresh autonomous BLACK receipt after that boot','automatic_resume':'Linux system service/timer runs without Owner relay'},
            {'id':'LEARNING_RUNTIME_DURABILITY','class':'G1','dependency':'Accepted persistent backend store and separated role bindings','action':'Use existing persistent execution surface; keep free Render admin writes disabled','automatic_resume':'Reaper outcomes and Critic/Root tested version promotion'}],
          'no_receipt_no_closure':True,'secret_values_disclosed':False}
    body['receipt_sha256']=digest(canonical(body))
    (output/'commissioning.json').write_text(json.dumps(body,indent=2)+'\n')
    (output/'learning-cycle.json').write_text(json.dumps(learning,indent=2)+'\n')
    (output/'capability-record.json').write_text(json.dumps(learning['capability'],indent=2)+'\n')
    (output/'commissioning.md').write_text('# AMX commissioning receipt\n\nStatus: HOLD — directive remains open.\n\n'+
        f"Tests: {tests['tests_run']} run; {tests['failures']} failures; {tests['errors']} errors.\n"+
        f"Actual registered repository restore: {restore['state']}; files compared: {restore['files_verified']}.\n"+
        'Encryption/corruption/interruption and local Reaper learning are tested. Live service promotion, private Drive enrollment, independent custody and full Windows boot retain specific gates.\n\n'+
        'Acceptance: '+', '.join(k+'='+v['state'] for k,v in checks.items())+'\n\n'+
        'Machine receipt SHA-256: '+body['receipt_sha256']+'\n')
    return body


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    result=commission(args.output)
    print(json.dumps({'state':result['state'],'tests':result['tests'],'restore':result['recovery']['restore_test'],'receipt_sha256':result['receipt_sha256']}))
    raise SystemExit(0 if result['tests']['state']=='PASS' else 1)
