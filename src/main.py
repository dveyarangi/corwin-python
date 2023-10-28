from fastapi import FastAPI
from pydantic import BaseModel
import virtualenv
import subprocess
import os
from utils import find_indices, merge_number_set, find_sequences
from typing import List, Dict

app = FastAPI()

TEST_PROCESS_NAME = "TestProcess"
STACKTRACE_SAMPLE_SIZE = 5

class CodeData(BaseModel):
    language: str
    function: List[str]
    test: List[str]
    imports: List[str]
    libraries: List[str]
    env: str

def extract_relevant_error(full_traceback: str) -> str:
    """
    Extract the most relevant error message and line from a full traceback.
    """
    lines = full_traceback.splitlines()
    error_line = ""
    error_message = "Unknown error"
    print("\n".join(lines))

    result = None

    if lines[-1].startswith("FAILED"):
        seps = find_indices(lines, lambda line: line.startswith("---------------------------------"))
        failed_tests_first, failed_tests_last = seps[0], seps[1]
        error_body = "\n".join(lines[failed_tests_first+1:failed_tests_last])
        error_message = lines[-1]

    else:
        error_body = ''
        all_relevant_indices:[int] = []
        roots_indices = find_indices(lines, lambda line: TEST_PROCESS_NAME in line)
        for index in roots_indices:
            relevant_indices = list(range(index-STACKTRACE_SAMPLE_SIZE, index+STACKTRACE_SAMPLE_SIZE+1))
            merge_number_set(relevant_indices, all_relevant_indices)

        sequences = find_sequences(all_relevant_indices, min_val=0, max_val=len(lines))

        error_body = ""
        for sstart, send in sequences:
            if sstart > 0:
                error_body +="...\n"
            error_body += "\n".join(lines[sstart:send]) + "\n"

        error_message = lines[-1]

    result = f"{error_body}\n{error_message}"

    return result

@app.post("/run_test/")
async def run_test(data: CodeData):
    env = data.env
    language = data.language.replace(" ", "_" )
    env_path = f"data/{language}/envs/{env}"
    libraries = data.libraries

    imports = "\n".join(data.imports)


    function = "\n".join(data.function)
    test = "\n".join(data.test)

    test_runner_code = """
print("===== TEST RESULTS START =====")
suite = unittest.TestLoader().loadTestsFromTestCase(TestProcess)
unittest.TextTestRunner().run(suite)
print("===== TEST RESULTS END =====")
    """
    test += test_runner_code



    # Create the virtual environment if it doesn't exist
    if not os.path.exists(env_path):
        virtualenv.cli_run([env_path])

    # Install the required packages
    if libraries:
        pip_path = os.path.join(env_path, "Scripts", "pip.exe")
        result = subprocess.run([pip_path, "install"] + libraries)
        if result.returncode == 0:
            print("Successfully installed packages")
        else:
            return {"outcome": "failure", "error": result.stderr}

    # Combine the function and test code
    combined_code = f"\n\n{imports}\n\n{function}\n\n{test}"

    # Execute the combined code in the virtual environment
    python_path = os.path.join(env_path, "Scripts", "python")
    result = subprocess.run([python_path, "-c", combined_code], capture_output=True, text=True)

    if result.returncode == 0 and not result.stderr:
        return {"outcome": "success"}

    if result.stderr.endswith("OK\n"):
        return {"outcome": "success"}
    error_message = extract_relevant_error(result.stderr)
    print(error_message)
    return {"outcome": "failure", "error": error_message}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7001)