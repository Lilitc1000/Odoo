### 环境设置 🛠️
需要使用如下命令将镜像的代码复制到本地后，启动容器，再选择Odoo Debugger开始调试
```shell
docker exec odoo_web tar -czvf /tmp/odoo.tar.gz /usr/lib/python3/dist-packages/odoo
docker cp odoo_web:/tmp/odoo.tar.gz .
docker exec odoo_web rm /tmp/odoo.tar.gz
tar -xzvf odoo.tar.gz -C .
```
