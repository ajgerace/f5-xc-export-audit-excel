# f5-xc-export-audit-excel
Export F5 Distributed Cloud (F5XC) Audit logs to an Excel spreadsheet

This script will accept arguments on the CLI for (tenant, token, namespace and hours) 

```
python3 f5-xc-export-audit-logs2excel.py --tenant <tenantName> --token <API Token> --namespace <namespace or ALL> --hours <1-720>
```

### Requirements:
Python Modules
- Openpyxl 
- Pandas 
- Requests

