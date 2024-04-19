import json
import os
from urllib.parse import urljoin, urlparse

import requests
import pandas as pd
import random
import string
import re
from tqdm import tqdm

def load_swagger_json(path):
    with open(path, 'r') as file:
        return json.load(file)

def generate_random_parameter(param):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def check_sensitive_data(structure):
    """检查结构体中是否包含敏感信息，如phone或address"""
    sensitive_keywords = ["phone", "address"]
    structure_str = json.dumps(structure).lower()
    return any(keyword in structure_str for keyword in sensitive_keywords)

def expand_ref(ref, components, visited_refs):
    ref_path = ref.split('/')
    ref_name = ref_path[-1]
    if ref_name in visited_refs:
        # 避免无限递归
        return {"$ref": ref_name}
    visited_refs.add(ref_name)
    return expand_structure(components["schemas"][ref_name], components, visited_refs)

def expand_structure(structure, components, visited_refs):
    if "type" in structure:
        if structure["type"] == "object":
            expanded = {}
            for prop, prop_def in structure.get("properties", {}).items():
                if "$ref" in prop_def:
                    expanded[prop] = expand_ref(prop_def["$ref"], components, visited_refs)
                else:
                    expanded[prop] = expand_structure(prop_def, components, visited_refs)
            return expanded
        elif structure["type"] == "array":
            items_def = structure.get("items", {})
            if "$ref" in items_def:
                return [expand_ref(items_def["$ref"], components, visited_refs)]
            else:
                return [expand_structure(items_def, components, visited_refs)]
        else:
            return structure.get("type")
    elif "$ref" in structure:
        return expand_ref(structure["$ref"], components, visited_refs)
    else:
        return structure

def get_api_response_structure(path, method, swagger_data):
    responses = swagger_data["paths"][path][method].get("responses", {})
    success_response = responses.get("200", {})
    if "content" in success_response:
        content_types = success_response["content"]
        schema = content_types.get("*/*", content_types.get("application/json", {})).get("schema", {})
        if "$ref" in schema:
            components = swagger_data.get("components", {})
            visited_refs = set()  # 初始化一个空集合来跟踪访问过的引用
            structure = expand_ref(schema["$ref"], components, visited_refs)
            return json.dumps(structure, indent=2)
    return "{}"


def send_request(host, path, method, parameters, swagger_data):
    url = f"{host}{path}"
    response_structure = "{}"
    contains_sensitive = False
    try:
        if method.lower() == "get":
            response = requests.get(url, params=parameters)
        elif method.lower() == "post":
            response = requests.post(url, data=parameters)
        else:
            print(f"Unsupported method: {method}")
            return method, path, "Unsupported Method", False, "{}"

        if response.status_code == 200:
            response_structure = get_api_response_structure(path, method.lower(), swagger_data)
            contains_sensitive = check_sensitive_data(json.loads(response_structure))
        return method, path, response.status_code, contains_sensitive, response_structure
    except Exception as e:
        print(f"Error sending request to {url}: {e}")
        return method, path, "Error", False, "{}"


def main(swagger_path, host):
    swagger_data = load_swagger_json(swagger_path)
    results = []

    # 获取所有API路径和方法，以便计算总进度
    total_apis = sum(len(methods.items()) for path, methods in swagger_data.get("paths", {}).items())

    progress_bar = tqdm(total=total_apis, desc="Scanning APIs", unit="API")

    for path, methods in swagger_data.get("paths", {}).items():
        for method, details in methods.items():
            parameters = {}
            for param in details.get("parameters", []):
                if param.get("in") == "query":
                    param_name = param.get("name")
                    parameters[param_name] = generate_random_parameter(param)
            result = send_request(host, path, method, parameters, swagger_data)
            results.append(result)
            progress_bar.update(1)  # 更新进度条

    df = pd.DataFrame(results, columns=["Method", "API URI", "Status Code", "Contains Sensitive", "Response Schema"])
    # 从swagger_data中提取title并生成文件名
    title = swagger_data.get("info", {}).get("title", "api_documentation")
    # 使用正则表达式移除非法字符
    safe_title = re.sub(r"[^a-zA-Z0-9 \n.]", "_", title)
    filename = f"{safe_title}.xlsx"
    df.to_excel(filename, index=False)
    print(f"Results saved to {filename}")

def load_paths():
    with open('swagger.txt', 'r') as file:
        return [line.strip() for line in file if line.strip()]

def save_swagger_document(url, data):
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    if not filename.endswith('.json'):
        filename += '.json'
    with open(filename, 'w') as f:
        json.dump(data, f)
    print(f"Saved {filename} from {url}")

def check_swagger_documents(base_url, paths):
    for path in paths:
        full_url = urljoin(base_url, path)
        try:
            response = requests.get(full_url, timeout=10)
            response.raise_for_status()  # 确保请求成功
            data = response.json()  # 尝试解析JSON数据
            if "swagger" in data or "openapi" in data:  # 检查是否是Swagger文档
                save_swagger_document(full_url, data)
                print(f"Swagger document found and saved from {full_url}")
                break  # 找到后不再继续检查其他路径
        except requests.exceptions.RequestException as e:
            print(f"Request failed for {full_url}: {e}")
        except json.JSONDecodeError:
            print(f"Failed to decode JSON from {full_url}")

def swagger_scan():
    paths = load_paths()
    with open('url.txt', 'r') as file:
        for base_url in file:
            base_url = base_url.strip()  # 去除可能的空白字符
            if base_url:
                check_swagger_documents(base_url, paths)

if __name__ == "__main__":
    # swagger_path = input("Enter the path to your local swagger.json file: ")
    # host = input("Enter the host address for API calls: ")
    # main(swagger_path, host)
    swagger_scan()
