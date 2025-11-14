import databricks
import time

def vs_endpoint_exists(vsc, endpoint_name):
    try:
        vsc.get_endpoint(endpoint_name)
        return True
    except Exception as e:
        if 'Not Found' in str(e):
            print(f'Unexpected error describing the endpoint. Try deleting it? vsc.delete_endpoint({endpoint_name}) and rerun the previous cell')
            raise e
        return False
    
def wait_for_vs_endpoint_to_be_ready(vsc, vs_endpoint_name):
  for i in range(180):
    endpoint = vsc.get_endpoint(vs_endpoint_name)
    status = endpoint.get("endpoint_status", endpoint.get("status"))["state"].upper()
    if "ONLINE" in status:
      return endpoint
    elif "PROVISIONING" in status or i <6:
      if i % 20 == 0: 
        print(f"Waiting for endpoint to be ready, this can take a few min... {endpoint}")
      time.sleep(10)
    else:
      raise Exception(f'''Error with the endpoint {vs_endpoint_name}. - this shouldn't happen: {endpoint}.\n Please delete it and re-run the previous cell: vsc.delete_endpoint("{vs_endpoint_name}")''')
  raise Exception(f"Timeout, your endpoint isn't ready yet: {vsc.get_endpoint(vs_endpoint_name)}")


def index_exists(vsc, endpoint_name, index_full_name):
    try:
        vsc.get_index(endpoint_name, index_full_name).describe()
        return True
    except Exception as e:
        if 'RESOURCE_DOES_NOT_EXIST' not in str(e):
            print(f'Unexpected error describing the index. This could be a permission issue. Try deleting it? vsc.delete_index({index_full_name})')
            raise e
        return False
    
def wait_for_index_to_be_ready(vsc, vs_endpoint_name, index_name):
  for i in range(180):
    idx = vsc.get_index(vs_endpoint_name, index_name).describe()
    index_status = idx.get('status', idx.get('index_status', {}))
    status = index_status.get('status', 'UNKOWN').upper()
    url = index_status.get('index_url', index_status.get('url', 'UNKOWN'))
    if "ONLINE" in status:
      return idx
    if "UNKOWN" in status:
      print(f"Can't get the status - will assume index is ready {idx} - url: {url}")
      return idx
    elif "PROVISIONING" in status:
      if i % 20 == 0: print(f"Waiting for index to be ready, this can take a few min... {index_status} - pipeline url:{url}")
      time.sleep(10)
    else:
        raise Exception(f'''Error with the index - this shouldn't happen. DLT pipeline might have been killed.\n Please delete it and re-run the previous cell: vsc.delete_index("{index_name}, {vs_endpoint_name}") \nIndex details: {idx}''')
  raise Exception(f"Timeout, your index isn't ready yet: {vsc.get_index(index_name, vs_endpoint_name)}")

def check_index_online(vs_index_fullname: str, vector_index: databricks.vector_search.index.VectorSearchIndex):
    for i in range(180):
        status = vector_index.describe()['status']["detailed_state"]
        if (status != "ONLINE" and status != "ONLINE_NO_PENDING_UPDATE"):
            print(f"Syncing {vs_index_fullname}")
            time.sleep(10)
        else:
            print(f"{vs_index_fullname} is now synced")
            return