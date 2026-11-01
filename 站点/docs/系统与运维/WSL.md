# WSL

本篇收录适用于 Linux 的 Windows 子系统（Windows Subsystem for Linux，WSL）在本机使用中的实际问题：完整 Linux 桌面、内存占用与开发容器按需启动、与 Windows 的文件互通、Zone.Identifier 文件处理。WSL 是 Windows 的子系统，属本机环境问题而非 Linux 系统管理；Linux 系统管理知识另见《Linux》。

## 在 Windows 本机打开 WSL 完整 Linux 桌面

**结论**：沿用现有发行版补装桌面组件——Xfce 加 xrdp、xorgxrdp，配置本机回环端口供 mstsc 连接；不另装发行版。

本机基础（2026-10-27 实测）：

- 已运行 Ubuntu 26.04.1 LTS（WSL 2），systemd、WSLg 与镜像网络的基础已具备。
- 未安装 Xfce、xrdp、xorgxrdp；只读依赖模拟成功，计划新增 348 个软件包且无卸载。
- 实际安装与桌面登录尚未验证。

方案取舍：

- WSLg 官方支持图形应用集成；应用窗口与完整 Linux 桌面分开理解。
- Kali 的 Win-KeX 仍是特定发行版备选。

版本口径——三个版本分别理解：

- WSL 软件包版本：本机 3.0.3.0。
- 发行版运行架构：WSL 1／WSL 2。微软当前文档列出的架构仍为这两种，没有对应的 WSL 3 发行版。
- Linux 发行版版本：Ubuntu 26.04.1 LTS。

附带变更：`.wslconfig` 中 `autoMemoryReclaim=gradual` 原放在 `[wsl2]`，已按用户要求于 2026-10-27 移入 `[experimental]` 并核对文件，其他配置已保留且已备份；尚未重启 WSL 或验证实际回收行为。

信源：

- [微软：WSL 图形应用支持及完整桌面限制（一手）](https://learn.microsoft.com/en-us/windows/wsl/tutorials/gui-apps)
- [Xfce 官方功能说明（一手）](https://xfce.org/about/)
- [xrdp 官方项目（一手）](https://github.com/neutrinolabs/xrdp)
- [微软：WSL 高级配置与 autoMemoryReclaim 所属配置段（一手）](https://learn.microsoft.com/en-us/windows/wsl/wsl-config)
- [微软：WSL 1 与 WSL 2 架构比较（一手）](https://learn.microsoft.com/en-us/windows/wsl/compare-versions)
- [微软：WSL 软件包 3.0.3 发布记录（一手）](https://github.com/microsoft/WSL/releases/tag/3.0.3)
- [Kali：Win-KeX（一手）](https://www.kali.org/docs/wsl/win-kex/)
- 本机实测（一手，2026-10-27）：`wsl --version`、`wsl --list --verbose`、`/etc/os-release`、`ps -p 1`、`apt-get -s install` 等命令输出

### 证据与时效 · q-20261027-001

- **信源**：[一手·本机实测，2026-10-27] `wsl --version`：WSL 3.0.3.0、WSLg 1.0.79、内核 6.18.54.1-1；`wsl --list --verbose`：唯一 Ubuntu 发行版，Running、版本 2；`/etc/os-release`：Ubuntu 26.04.1 LTS、amd64；`ps -p 1`：systemd；`dpkg-query` 与桌面会话目录检查：无 Xfce、xrdp、xorgxrdp 和桌面会话；`apt-cache policy`：xfce4 4.20.1、xrdp 0.10.1-4.1ubuntu0.1、xorgxrdp 1:0.10.2-1build1；`apt-get -s install xfce4 xfce4-goodies xrdp xorgxrdp`：退出码 0，新增 348、卸载 0；`wslinfo --networking-mode`：mirrored；`free -h`：WSL 总内存约 15 GiB、可用约 9.3 GiB；Windows CIM：Windows 11 家庭版中文版、构建 26300.9711、物理内存约 31.5 GiB、16 个逻辑处理器；Ubuntu 虚拟磁盘在 D 盘，宿主卷剩余约 404.2 GiB；Windows 与 Linux 均未监听检查时的 3389、3390、5900、5901 端口；[一手] [微软：WSL 图形应用支持及完整桌面限制](https://learn.microsoft.com/en-us/windows/wsl/tutorials/gui-apps)；[一手] [Xfce 官方功能说明](https://xfce.org/about/)；[一手] [xrdp 官方项目](https://github.com/neutrinolabs/xrdp)；[一手] [微软：WSL 网络与 localhost 访问](https://learn.microsoft.com/en-us/windows/wsl/networking)；[一手] [微软：WSL 高级配置与 autoMemoryReclaim 所属配置段](https://learn.microsoft.com/en-us/windows/wsl/wsl-config)；[一手] [微软：WSL 命令及版本参数含义](https://learn.microsoft.com/en-us/windows/wsl/basic-commands)；[一手] [微软：WSL 1 与 WSL 2 架构比较](https://learn.microsoft.com/en-us/windows/wsl/compare-versions)；[一手] [微软：WSL 软件包 3.0.3 发布记录](https://github.com/microsoft/WSL/releases/tag/3.0.3)；[一手] [微软：WSL systemd 支持](https://learn.microsoft.com/en-us/windows/wsl/systemd)；[一手] [Kali：Win-KeX](https://www.kali.org/docs/wsl/win-kex/)；[一手] [微软：WSL 常见问题及家庭版支持](https://learn.microsoft.com/en-us/windows/wsl/faq)；[一手] [微软：远程桌面客户端与主机的版本条件](https://support.microsoft.com/en-us/windows/experience/connectivity-networking/how-to-use-remote-desktop)

## WSL 内存占用与开发容器按需启动

**结论**：`autoMemoryReclaim=gradual` 只针对缓存回收，不能替代停止不需要的应用；配置修改也须等 WSL 重启生效。应用内存、缓存和宿主工作集分别诊断。

背景：本机 WSL 同时运行七个开发容器与多个 AI 进程，并保留文件缓存。

处置（2026-10-27，只代表当时状态）：

- 将 SQL Server、MySQL、Nacos、RabbitMQ、Redis、Qdrant、Ollama 的容器及对应 Compose 的重启策略设为 `"no"` 并正常停止，数据保留。
- WSL 内部已用由约 7.1 GiB 降至约 3.0 GiB。
- 剩余约 4.3 GiB 文件缓存及仍在活动的 AI 进程，使宿主占用不会立即降至同一数字。
- gradual 回收仍待 WSL 重启验证。

信源：

- [微软 WSL 配置（一手）](https://learn.microsoft.com/en-us/windows/wsl/wsl-config)
- [Docker restart 策略（一手）](https://docs.docker.com/reference/compose-file/services/#restart)
- [Docker 容器内存限制（一手）](https://docs.docker.com/engine/containers/resource_constraints/)
- [Linux 内核关于缓存回收的说明（一手）](https://docs.kernel.org/admin-guide/sysctl/vm.html#drop-caches)
- 本机实测（一手，2026-10-27）：`Get-Process`、Windows 性能内存计数器、`/proc/meminfo`、`free`、`docker stats`、`docker inspect`

### 证据与时效 · q-20261027-002

- **信源**：[一手·本机实测，2026-10-27] `Get-Process`、Windows 性能内存计数器、WSL `/proc/meminfo`、`free`、`docker stats`、`docker inspect` 与 Compose 校验；详细测量、限制及变更记录见关联的 Windows 条目；[一手] [微软 WSL 配置](https://learn.microsoft.com/en-us/windows/wsl/wsl-config)；[一手] [Docker restart 策略](https://docs.docker.com/reference/compose-file/services/#restart)；[一手] [Docker 容器内存限制](https://docs.docker.com/engine/containers/resource_constraints/)；[一手] [Linux 内核关于缓存回收的说明](https://docs.kernel.org/admin-guide/sysctl/vm.html#drop-caches)

## Windows 与 WSL 的文件互通

**结论**：不需要同步技术——两侧访问的是同一份存储，即写即见，不是两份拷贝。

| 访问方 | NTFS：Windows 盘 | ext4：WSL 2 内 |
| --- | --- | --- |
| Windows 应用 | 同侧直接读写：快 | 经 `\\wsl$` 路径：9P，慢 |
| Linux 进程 | 经 `/mnt/c` 挂载：9P，慢 | 同侧直接读写：快 |

- Windows 经 `\\wsl$\` 或 `\\wsl.localhost\` 路径读写 WSL 的 ext4 文件系统。
- WSL 经 `/mnt/c` 挂载读写 NTFS。
- 跨界读写经 9P 协议，明显慢于同侧访问。

限制：

- Windows 侧对 `/mnt/c` 下文件的修改不触发 Linux 侧 inotify 事件，热重载与文件监听失效（microsoft/WSL #4739，2019 年开；新版 WSL 是否修复未核实）。
- 官方建议项目文件与工具同侧存放：Linux 项目放 `~/`，用 VS Code Remote-WSL 扩展在 Windows 编辑。
- 仅当确需两份独立拷贝时才用 Syncthing、Unison、rsync 等同步工具（适用性未核实）。

适用条件：上述结论针对 WSL 2（轻量虚拟机架构）；WSL 1 直接访问 Windows 文件系统，跨界性能特征不同。`\\wsl$\` 路径仅在发行版运行时可用；`\\wsl.localhost` 在 Windows 11 可自动拉起发行版。

信源：

- [微软：WSL interop——Windows 与 Linux 集成（一手）](https://learn.microsoft.com/en-us/windows/dev-environment/wsl/interop)
- [微软：跨文件系统工作（一手）](https://learn.microsoft.com/en-us/windows/wsl/filesystems)
- [微软：VS Code 与 WSL 入门（一手）](https://learn.microsoft.com/en-us/windows/wsl/tutorials/wsl-vscode)
- [microsoft/WSL #4739：Windows 应用对 Windows 盘文件的修改不触发 inotify（一手）](https://github.com/microsoft/WSL/issues/4739)

### 证据与时效 · q-20261029-003

- **信源**：[一手] [WSL interop — Windows and Linux integration](https://learn.microsoft.com/en-us/windows/dev-environment/wsl-interop)；[一手] [Working across file systems](https://learn.microsoft.com/en-us/windows/wsl/filesystems)；[一手] [Comparing WSL Versions](https://learn.microsoft.com/en-us/windows/wsl/compare-versions)；[一手] [Get started using VS Code with WSL](https://learn.microsoft.com/en-us/windows/wsl/tutorials/wsl-vscode)；[一手] [microsoft/WSL Issue #4739：Windows 应用对 Windows 盘文件的修改不触发 inotify](https://github.com/microsoft/WSL/issues/4739)
- **核实**：2026-10-29；核实两侧访问路径、9P 协议、跨界性能对比与同侧存放建议（wsl-interop 页 ms.date 2026-07-16、compare-versions 页）、VS Code Remote-WSL 客户端-服务端架构（wsl-vscode 页 ms.date 2026-04-15）。inotify 限制依据官方仓库 2019 年开的 Issue #4739，新版 WSL 是否修复未核实。适用条件：WSL2（轻量虚拟机架构）；WSL1 直接访问 Windows 文件系统，跨界性能特征不同。`\\wsl$\` 路径仅在发行版运行时可用，`\\wsl.localhost` 在 Windows 11 可自动拉起发行版。

## `文件名:Zone.Identifier` 文件的来历与处理

**结论**：`文件名:Zone.Identifier` 是已知 WSL bug 的产物；删除无害，加入 `.gitignore` 防入库。

来历链条：

1. `Zone.Identifier` 是 NTFS 交替数据流（Alternate Data Stream，ADS），是 Windows 给网络下载文件附加的网页标记（Mark of the Web，MOTW），内容形如 `[ZoneTransfer] ZoneId=3`。
2. ZoneId 3 对应 Internet 区域。URLZONE 枚举：0 本机、1 内网、2 受信任、3 Internet、4 不受信任。
3. 文件在 Windows 侧下载获得 MOTW，再经资源管理器拖拽或复制进 `\\wsl$`。
4. ext4 不支持 ADS；Explorer 写入该流时 WSL 未正确处理，把流物化成独立的 `文件名:Zone.Identifier` 文件。
5. 这是 microsoft/WSL #4609（2019 年开、2026-03 微软重开）记录的已知 bug，标签含 bug、file system、fixedininsiderbuilds。

本机实测：仓库内 72 个该类文件，内容均为 `ZoneId=3`。

处理与预防：

- 删除无害：`find . -name "*:Zone.Identifier" -type f -delete`。
- `.gitignore` 加 `*:Zone.Identifier`。
- 预防：把 `wsl.localhost` 加入本地 Intranet 站点，或在 Windows 侧先 Unblock。

清理记录（2026-10-30，经用户确认）：删除 `/home/luguosong/code-wsl/personal` 下 4 个项目共 6369 个（视频制作 6022、知识学习 335、图片海报设计 11、书籍翻译 1），删除前逐个校验内容均含 `ZoneTransfer`，删后复查为 0；同日清除 `code-wsl/company/uocs-project` 下 899 个，复查为 0。

信源：

- [microsoft/WSL #4609（一手）](https://github.com/microsoft/WSL/issues/4609)
- [URLZONE 枚举（Urlmon.h，MS Learn 归档）（一手）](https://learn.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/platform-apis/ms537175(v=vs.85))
- 本机实测（一手，2026-10-30）：仓库内 72 个该类文件的 `cat` 内容

### 证据与时效 · q-20261030-001

- **信源**：[一手·本机实测，2026-10-30] 仓库内 72 个该类文件的 `cat` 内容；[一手] [microsoft/WSL #4609](https://github.com/microsoft/WSL/issues/4609)；[一手] [URLZONE enumeration（Urlmon.h，MS Learn 归档）](https://learn.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/platform-apis/ms537175(v=vs.85))；[二手·仅定位] [WSL #7456](https://github.com/microsoft/WSL/issues/7456)


## 提问记录

### q-20261027-001

- **原题**：2026-10-27 · 在 Windows 本机打开 WSL 完整 Linux 桌面的方案选择
- **问**：wsl 可视桌面化远程方案；已澄清为在当前 Windows 上打开完整 Linux 桌面；追问：探测当前电脑 WSL 情况并给出建议；WSL 3.0.3.0 是否有对应的 WSL 3 发行版。
- **领域**：Linux
- **首次**：2026-10-27
- **更新**：2026-10-27
- **正文**：[在 Windows 本机打开 WSL 完整 Linux 桌面](#在-windows-本机打开-wsl-完整-linux-桌面)
- **关联**：[2026-10-26 · Windows 11 专业版与家庭版的主要区别及选型](Windows.md#q-20261026-009)；[2026-10-23 · 零基础学习 Linux 的学习计划与资源组合](Linux.md#q-20261023-001)

### q-20261027-002

- **原题**：2026-10-27 · WSL 内存占用、缓存回收与开发容器按需启动
- **问**：Windows 内存升高与 WSL 的关系；七个开发用 Docker 服务要求取消常驻，使用时再启动。
- **领域**：Linux
- **首次**：2026-10-27
- **更新**：2026-10-27
- **正文**：[WSL 内存占用与开发容器按需启动](#wsl-内存占用与开发容器按需启动)
- **关联**：[2026-10-27 · Windows 内存清理后回涨与 WSL 常驻服务的占用诊断](Windows.md#q-20261027-004)；[2026-10-27 · 在 Windows 本机打开 WSL 完整 Linux 桌面的方案选择](WSL.md#q-20261027-001)；[本机开发服务启停工具](../附件/工具/开发服务.ps1)

### q-20261029-003

- **原题**：2026-10-29 · Windows 与 WSL 之间文件实时同步的技术
- **问**：有没有文件在 Windows 端和 WSL 端实时同步的技术。
- **领域**：Linux
- **首次**：2026-10-29
- **更新**：2026-10-29
- **正文**：[Windows 与 WSL 的文件互通](#windows-与-wsl-的文件互通)
- **关联**：[2026-10-27 · WSL 内存占用、缓存回收与开发容器按需启动](WSL.md#q-20261027-002)；[2026-10-27 · 在 Windows 本机打开 WSL 完整 Linux 桌面的方案选择](WSL.md#q-20261027-001)

### q-20261030-001

- **原题**：2026-10-30 · WSL 内 `文件名:Zone.Identifier` 文件的来历与处理
- **问**：仓库里为什么出现 `.gitignore:Zone.Identifier`、`AGENTS.md:Zone.Identifier` 这类文件。
- **领域**：Linux
- **首次**：2026-10-30
- **更新**：2026-10-30
- **正文**：[`文件名:Zone.Identifier` 文件的来历与处理](#文件名zoneidentifier-文件的来历与处理)
- **关联**：[2026-10-27 · WSL 内存占用、缓存回收与开发容器按需启动](WSL.md#q-20261027-002)（同为本机 WSL 主题）
