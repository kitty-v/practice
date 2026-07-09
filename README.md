# Start our go language study

> [!TIP]
> **Keep going**<br>
> **study every day**

---

> [!IMPORTANT]
> please use url to download golang
> ```bash
> wget https://go.dev/dl/go1.22.5.linux-amd64.tar.gz
> sudo rm -rf /usr/local/go
> sudo tar -C /usr/local -xzf go1.22.5.linux-amd64.tar.gz
> echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
> source ~/.bashrc
> ```

---

## project before exec blow in your termainal
```bash
go mod init practice
go get github.com/go-sql-driver/mysql
```
## start our first go file
```go
package main
import "fmt"
func main(){
    const name = "Jac"
    const age = 21
    var a int
    a = 1
    fmt.Println(name)
    
    for a <= 10 {
    fmt.Println(a)
    a++
}
}
```
