# f5-xc-export-audit-excel
Export F5 Distributed Cloud (F5XC) Audit logs to an Excel spreadsheet

This script will accept arguments on the CLI for (tenant, token, namespace and hours) 

```
python3 f5-xc-export-audit-logs2excel.py --tenant <tenantName> --token <API Token> --namespace <namespace or ALL> --hours <1-720>
```

### F5 XC Documentation - Credentials

[Credentials] (https://docs.cloud.f5.com/docs-v2/administration/how-tos/user-mgmt/Credentials)
- Click on "Generate API Tokens for My Credentials" on the right-hand side or scroll down to this section 

### Requirements:
Python Modules
- Openpyxl 
- Pandas 
- Requests

