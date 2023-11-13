# odoo-sh-template
Common template to quickly setup an odoo.sh demo/production
# Usage
Simply create a repository using this template. Depending on your agreement with your customer you can opt to delete and keep only the modules that will be deployed for that project.
# Maintenance/Update
This repository is updated periodically to the latest repos. Since it's not a fork any repository that you create using this template will not update or offer to merge with this one.
If you want to update a specific repository after it was created using this template, please run 
```
git submodule update --init --recursive
git submodule update --remote --recursive
git commit -a -m "[UPD] submodules"
git push
