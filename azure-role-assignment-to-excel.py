import json
import subprocess
import pandas as pd

sub_cmd = "az account show --query id -o tsv"
subscription_id = subprocess.run(sub_cmd, shell=True, capture_output=True, text=True).stdout.strip()

cmd = "az role assignment list --all"
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

role_assignments = json.loads(result.stdout)

azure_portal_url = "https://portal.azure.com/#@pmi.org/resource"

data = []
for role in role_assignments:
    principal_id = role.get("principalId", "N/A")
    principal_name = role.get("principalName", "Unknown")
    scope = role.get("scope", "")
    
    full_scope_url = f"{azure_portal_url}{scope}" if scope else "N/A"

    if principal_name == "Unknown" and principal_id != "N/A":
        fetch_name_cmd = f"az ad sp show --id {principal_id} --query displayName -o tsv"
        try:
            principal_name = subprocess.run(fetch_name_cmd, shell=True, capture_output=True, text=True).stdout.strip()
        except Exception:
            principal_name = "Unknown"

    data.append({
        "Subscription ID": subscription_id,
        "Principal ID": principal_id,
        "Principal Name": principal_name,
        "Principal Type": role.get("principalType"),
        "Role Definition Name": role.get("roleDefinitionName"),
        "Scope URL": full_scope_url,
        "Resource Group": role.get("resourceGroup", "N/A"),
        "Created By": role.get("createdBy"),
        "Created On": role.get("createdOn"),
        "Updated By": role.get("updatedBy"),
        "Updated On": role.get("updatedOn"),
        "Description": role.get("description", ""),
    })

df = pd.DataFrame(data)

output_file = "azure-role-assignments.xlsx"
df.to_excel(output_file, index=False)

print(f"Exported role assignments to {output_file}")
