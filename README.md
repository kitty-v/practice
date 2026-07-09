# Start our go language study

> [!TIP]
> **Keep going**<br>
> **study every day**

---

[!IMPORTANT]
> **安装 Go 请使用官方最新版本，不要用 apt 安装！**
> 
> apt 仓库中的版本通常过旧，会导致某些特性不支持。
> 
> 推荐方式：
> ```bash
> wget https://go.dev/dl/go1.22.5.linux-amd64.tar.gz
> sudo rm -rf /usr/local/go
> sudo tar -C /usr/local -xzf go1.22.5.linux-amd64.tar.gz
> echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
> source ~/.bashrc
> ```

---

## 项目初始化
```bash
go mod init practice
go get github.com/go-sql-driver/mysql
