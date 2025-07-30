# isort:off
import sys
sys.path.append('CybersecurityBenchmarks')
# isort:on
import argparse
from tqdm import tqdm
import os
from insecure_code_detector import insecure_code_detector
import json
from insecure_code_detector import languages
import asyncio

parser = argparse.ArgumentParser(description='Merge multiple inference results into one file')
parser.add_argument('--fin', type=str, help='input file', default='')
parser.add_argument('--fout', type=str, help='output file', default='')
parser.add_argument('--n_worker', type=int, default=16)
args = parser.parse_args()

if args.fout == '':
    args.fout = f'{args.fin}.detected.jsonl'

data_in = [json.loads(line) for line in tqdm(open(args.fin, 'r'))]

language_map = {
    'c': languages.Language.C,
    'cpp': languages.Language.CPP,
    'csharp': languages.Language.CSHARP,
    'java': languages.Language.JAVA,
    'javascript': languages.Language.JAVASCRIPT,
    'php': languages.Language.PHP,
    'rust': languages.Language.RUST,
    'python': languages.Language.PYTHON
}


def detect_one(entry):    
    current_lang_str = entry['lang']
    current_lang = language_map[current_lang_str]
    code_detected_entries = []
    local_safe_cnt = 0
    local_error_cnt = 0
    for code in entry['code_blocks']:
        try:
            detection_results = asyncio.run(asyncio.wait_for(insecure_code_detector.analyze(current_lang, code), timeout=30))
        except asyncio.TimeoutError:
            print(f'Timeout for {current_lang_str} code block, skipping...')
            continue
        if detection_results == []:
            local_safe_cnt += 1
        else:
            local_error_cnt += 1
        code_detected_entries.append(
            {
                'code': code,
                'detection_results': [{
                    'cwe_id': iss.cwe_id,
                    'analyzer': str(iss.analyzer),
                    'rule': iss.rule,
                    'pattern_id': iss.pattern_id,
                } for iss in detection_results]
            }
        )

    ret_entry = {
        'lang': current_lang_str,        
        'code_detected_entries': code_detected_entries,
        'local_safe_cnt': local_safe_cnt,
        'local_error_cnt': local_error_cnt,
        **entry
    }
    del ret_entry['code_blocks']
    return ret_entry



fout = open(args.fout, 'w')

status_err = 0
status_safe = 0
has_safe = 0
not_has_safe = 0

from multiprocessing import Pool

pool = Pool(args.n_worker)
results = pool.imap_unordered(detect_one, tqdm(data_in, desc='Detecting', total=len(data_in), position=0))

pbar = tqdm(total=len(data_in), position=1, desc='Writing')
for ret_entry in results:
    local_error_cnt = ret_entry['local_error_cnt']
    local_safe_cnt = ret_entry['local_safe_cnt']
    del ret_entry['local_error_cnt']
    del ret_entry['local_safe_cnt']
    fout.write(json.dumps(ret_entry) + '\n')
    fout.flush()
    status_err += local_error_cnt
    status_safe += local_safe_cnt
    if local_safe_cnt > 0:
        has_safe += 1
    else:
        not_has_safe += 1
    pbar.update(1)
    pbar.set_postfix({'err': status_err, 'safe': status_safe, 'has_safe': has_safe, 'not_has_safe': not_has_safe})

fout.close()