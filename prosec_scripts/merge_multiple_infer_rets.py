import json
from tqdm import tqdm
import glob
import os

dir_in = 'infer-ret-claude-haiku-inst-phi3m-ori-task'
fout_name = 'infer-ret-claude-haiku-inst-phi3m-ori-task/infer-ret-all.phi3m-inst.jsonl'


# recursively find all files in the directory
flist_fnames = glob.glob(f'{dir_in}/**/*.jsonl', recursive=True)
flist = []
for fname in flist_fnames:    
    base_name = os.path.basename(fname)
    if base_name == os.path.basename(fout_name):
        continue
    base_name_wo_ext = os.path.splitext(base_name)[0]
    # remove infer-ret-
    base_name_wo_ext_wo_pfx = base_name_wo_ext.replace('infer-ret-', '')
    # base_name_wo_ext_wo_pfx = base_name_wo_ext.replace('infer-ret-ori-task-', '')
    # split by '-'
    parts = base_name_wo_ext_wo_pfx.split('-')
    cwe = parts[0]
    # convert cwe from cweXXX to CWE-XXX
    cwe = f'CWE-{cwe[3:]}'
    lang = parts[1]
    flist.append((fname, lang, cwe))


print()


def parse_code_blocks(text):
    code_blocks = []
    in_code_block = False
    for line in text.split('\n'):
        if '```' in line:
            in_code_block = not in_code_block
        elif in_code_block:
            code_blocks.append(line)
    return '\n'.join(code_blocks)


fout = open(fout_name, 'w')
for fpath, lang, cwe in tqdm(flist):
    for line in open(fpath, 'r'):
        entry = json.loads(line)
        code_blocks = [parse_code_blocks(r) for r in entry['responses']]
        code_blocks = [r for r in code_blocks if r.strip()!='']
        entry['code_blocks'] = code_blocks
        entry['lang'] = lang
        entry['cwe'] = cwe
        fout.write(json.dumps(entry) + '\n')
fout.close()