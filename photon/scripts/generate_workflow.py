import argparse
import requests
import json
import os


def main():
    p = argparse.ArgumentParser(description='Call /workflow/generate and save returned notebook')
    p.add_argument('--dataset-url', required=True)
    p.add_argument('--dataset-format', required=True)
    p.add_argument('--variable', required=True)
    p.add_argument('--title', default='Generated Workflow')
    p.add_argument('--api-url', default='http://127.0.0.1:8000/workflow/generate')
    p.add_argument('--api-key', default=None)
    p.add_argument('--out', default=None, help='Output path for the notebook (.ipynb)')
    args = p.parse_args()

    payload = {
        'dataset_url': args.dataset_url,
        'dataset_format': args.dataset_format,
        'variable': args.variable,
        'title': args.title,
    }

    headers = {'Content-Type': 'application/json'}
    if args.api_key:
        headers['x-api-key'] = args.api_key

    try:
        r = requests.post(args.api_url, json=payload, headers=headers, timeout=60)
    except Exception as e:
        print('Request failed:', e)
        raise

    print('Status:', r.status_code)
    if r.status_code != 200:
        print(r.text)
        return

    parsed = r.json()
    nb_json = parsed.get('notebook')
    if not nb_json:
        print("No 'notebook' field in response:", parsed)
        return

    out_path = args.out
    if not out_path:
        script_dir = os.path.dirname(__file__)
        out_path = os.path.normpath(os.path.join(script_dir, '..', 'data', 'generated_notebook.ipynb'))

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(nb_json)
    print('Saved notebook to', out_path)


if __name__ == '__main__':
    main()