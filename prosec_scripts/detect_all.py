# isort:off
import sys

sys.path.append('CybersecurityBenchmarks')
# isort:on
import argparse
import asyncio
import json
import os

from insecure_code_detector import insecure_code_detector, languages
from tqdm import tqdm

parser = argparse.ArgumentParser(description='Merge multiple inference results into one file')
parser.add_argument('--fin', type=str, help='input file', default='')
parser.add_argument('--fout', type=str, help='output file', default='')

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


def parse_code_blocks(text):
    code_blocks = []
    in_code_block = False
    for line in text.split('\n'):
        if '```' in line:
            in_code_block = not in_code_block
        elif in_code_block:
            code_blocks.append(line)
    return '\n'.join(code_blocks)

def detect_one(entry):
    ret_entries = []
    current_lang_str = entry['lang']
    current_lang = language_map[current_lang_str]
    local_err_cnt = 0
    local_safe_cnt = 0
    if 'code_blocks' not in entry:        
        code_blocks = [parse_code_blocks(r) for r in entry['responses']]
        entry['code_blocks'] = code_blocks

    for code in entry['code_blocks']:        
        try:
            detection_results = asyncio.run(asyncio.wait_for(insecure_code_detector.analyze(current_lang, code), timeout=30))
        except asyncio.TimeoutError:
            print(f'TimeoutError for {current_lang_str} code block, skipping...')
            continue
            # detection_results = []
        if detection_results == []:
            local_safe_cnt += 1
        else:
            local_err_cnt += 1
        detection_ret = [{
            'cwe_id': iss.cwe_id,
            'analyzer': str(iss.analyzer),
            'rule': iss.rule,
            'pattern_id': iss.pattern_id,
        } for iss in detection_results]
        ret_entry = {
            'lang': current_lang_str,
            'cwe': entry['cwe'],
            'code': code,
            'prompt': entry['prompt'],
            'detection_results': detection_ret
        }
        ret_entries.append(ret_entry)
    return {
        'ret_entries': ret_entries,
        'local_err_cnt': local_err_cnt,
        'local_safe_cnt': local_safe_cnt        
    }

fout = open(args.fout, 'w')
status_err = 0
status_safe = 0

from multiprocessing import Pool

pool = Pool(48)
results = pool.imap(detect_one, data_in)
# print status on tqdm bar
pbar = tqdm(total=len(data_in))
for ret in results:
    for ret_entry in ret['ret_entries']:
        fout.write(json.dumps(ret_entry) + '\n')
        fout.flush()
    status_err += ret['local_err_cnt']
    status_safe += ret['local_safe_cnt']
    pbar.update(1)
    # print pbar status
    pbar.set_postfix({'err': status_err, 'safe': status_safe})

pbar.close()
fout.close()