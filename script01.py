import subprocess  # Para ejecutar comandos del sistema
import json  # Para manejar JSON
import os  # Para manejar operaciones del sistema operativo como verificar la existencia de archivos
import shutil  # Para encontrar rutas de ejecutables

# Función para ejecutar un comando en el sistema
def run_command(command, cwd=None):
    try:
        # Ejecuta el comando con las opciones especificadas
        result = subprocess.run(command, cwd=cwd, shell=False, capture_output=True, text=True, check=True, encoding='latin-1')
        stdout = result.stdout.strip()  # Captura y limpia la salida estándar
        stderr = result.stderr.strip()  # Captura y limpia la salida de error
        return {"stdout": stdout, "stderr": stderr}  # Devuelve la salida en un diccionario
    except subprocess.CalledProcessError as e:
        # Manejo de errores cuando el comando falla
        stdout = e.stdout.strip() if e.stdout else ""
        stderr = e.stderr.strip() if e.stderr else ""
        return {"stdout": stdout, "stderr": f"Error running command: {e}. Stderr: {stderr}"}
    except FileNotFoundError as e:
        # Manejo de errores cuando el ejecutable no se encuentra
        return {"stdout": "", "stderr": f"Executable not found: {e}"}

# Función para validar un archivo de configuración usando kube-linter
def validate_with_kube_linter(config_file):
    kube_linter_exe = shutil.which('kube-linter')  # Encuentra la ruta del ejecutable kube-linter
    if not kube_linter_exe:
        return {"stdout": "", "stderr": "kube-linter executable not found"}
    return run_command([kube_linter_exe, 'lint', config_file])  # Ejecuta el comando de validación

# Función para validar un archivo de configuración usando Polaris
def validate_with_polaris(config_file):
    polaris_exe = 'C:/projects/validators/polaris/polaris.exe'  # Ruta fija del ejecutable Polaris
    if not os.path.exists(polaris_exe):
        return {"stdout": "", "stderr": f"Polaris executable not found at {polaris_exe}"}
    polaris_command = [polaris_exe, 'audit', '--audit-path', config_file]  # Comando de validación con Polaris
    return run_command(polaris_command, cwd='C:/projects/validators/polaris')  # Ejecuta el comando en el directorio especificado

# Función para validar un archivo de configuración usando Checkov
def validate_with_checkov(config_file):
    checkov_exe = shutil.which('checkov') or shutil.which('checkov.exe') or shutil.which('checkov.cmd')  # Encuentra la ruta del ejecutable checkov
    if not checkov_exe:
        return {"stdout": "", "stderr": "checkov executable not found"}
    return run_command([checkov_exe, '-f', config_file])  # Ejecuta el comando de validación

# Función para validar un archivo de configuración usando kube-score
def validate_with_kube_score(config_file):
    kube_score_exe = 'C:/projects/validators/kube-score/kube-score.exe'  # Ruta fija del ejecutable kube-score
    if not os.path.exists(kube_score_exe):
        return {"stdout": "", "stderr": f"kube-score executable not found at {kube_score_exe}"}
    return run_command([kube_score_exe, 'score', config_file])  # Ejecuta el comando de validación

# Función para formatear los resultados de manera más legible
def pretty_format_results(results):
    formatted_results = {}
    for tool, output in results.items():
        formatted_output = (
            f"Results for {tool}:\n"
            f"Standard Output:\n{output['stdout']}\n\n"
            f"Standard Error:\n{output['stderr']}\n\n"
            + "="*80 + "\n"
        )
        formatted_results[tool] = formatted_output  # Agrega el resultado formateado al diccionario
    return formatted_results

# Archivo de configuración a validar
config_file = '00privileges.yaml'
results = {}

# Ejecuta validaciones con diferentes herramientas y guarda los resultados
results['kube_linter'] = validate_with_kube_linter(config_file)
results['polaris'] = validate_with_polaris(config_file)
results['checkov'] = validate_with_checkov(config_file)
results['kube_score'] = validate_with_kube_score(config_file)

# Formatea los resultados para presentación
pretty_results = pretty_format_results(results)

# Guarda los resultados formateados en un archivo JSON
with open('validation_results.json', 'w') as f:
    json.dump(pretty_results, f, indent=4)

# Imprime los resultados formateados en la consola
for tool, output in pretty_results.items():
    print(output)
