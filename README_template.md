# SingBox Rules

这个仓库包含了从常用的Clash规则源自动转换生成的SingBox规则集。

## 规则来源

- [ACL4SSR/ACL4SSR](https://github.com/ACL4SSR/ACL4SSR) (master分支)
- [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)

## 使用方法

在SingBox配置中添加规则集：

```json
{
  "route": {
    "rule_set": [
      {
        "tag": "规则名称",
        "type": "remote",
        "format": "binary",
        "url": "https://raw.githubusercontent.com/*.srs",
        "download_detour": "proxy"
      }
    ],
    "rules": [
      {
        "rule_set": ["规则名称"],
        "outbound": "proxy或direct或block"
      }
    ]
  }
}
```

## 自动更新

规则每天自动更新一次。也可以手动触发GitHub Actions工作流来更新规则。
