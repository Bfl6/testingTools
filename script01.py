import subprocess
import json
import os
import shutil

def run_command(command, cwd=None):
    try:
        result = subprocess.run(command, cwd=cwd, shell=False, capture_output=True, text=True, check=True, encoding='latin-1')
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        return {"stdout": stdout, "stderr": stderr}
    except subprocess.CalledProcessError as e:
        stdout = e.stdout.strip() if e.stdout else ""
        stderr = e.stderr.strip() if e.stderr else ""
        return {"stdout": stdout, "stderr": f"Error running command: {e}. Stderr: {stderr}"}
    except FileNotFoundError as e:
        return {"stdout": "", "stderr": f"Executable not found: {e}"}

def validate_with_kube_linter(config_file):
    kube_linter_exe = shutil.which('kube-linter')
    if not kube_linter_exe:
        return {"stdout": "", "stderr": "kube-linter executable not found"}
    return run_command([kube_linter_exe, 'lint', config_file])

def validate_with_polaris(config_file):
    polaris_exe = 'C:/projects/validators/polaris/polaris.exe'
    if not os.path.exists(polaris_exe):
        return {"stdout": "", "stderr": f"Polaris executable not found at {polaris_exe}"}
    polaris_command = [polaris_exe, 'audit', '--audit-path', config_file]
    return run_command(polaris_command, cwd='C:/projects/validators/polaris')

def validate_with_checkov(config_file):
    checkov_exe = shutil.which('checkov') or shutil.which('checkov.exe') or shutil.which('checkov.cmd')
    if not checkov_exe:
        return {"stdout": "", "stderr": "checkov executable not found"}
    return run_command([checkov_exe, '-f', config_file])

def validate_with_kube_score(config_file):
    kube_score_exe = 'C:/projects/validators/kube-score/kube-score.exe'
    if not os.path.exists(kube_score_exe):
        return {"stdout": "", "stderr": f"kube-score executable not found at {kube_score_exe}"}
    return run_command([kube_score_exe, 'score', config_file])

def pretty_format_results(results):
    formatted_results = {}
    for tool, output in results.items():
        formatted_output = (
            f"Results for {tool}:\n"
            f"Standard Output:\n{output['stdout']}\n\n"
            f"Standard Error:\n{output['stderr']}\n\n"
            + "="*80 + "\n"
        )
        formatted_results[tool] = formatted_output
    return formatted_results

config_file = '00privileges.yaml'
results = {}

results['kube_linter'] = validate_with_kube_linter(config_file)
results['polaris'] = validate_with_polaris(config_file)
results['checkov'] = validate_with_checkov(config_file)
results['kube_score'] = validate_with_kube_score(config_file)

# Pretty print results
pretty_results = pretty_format_results(results)

# Save pretty results to a JSON file
with open('validation_results.json', 'w') as f:
    json.dump(pretty_results, f, indent=4)

# Print pretty results to console
for tool, output in pretty_results.items():
    print(output)
