# Linux

本领域记录 Linux 学习与实践：主线从命令行、文件权限、进程与启动进入存储、网络、安全、诊断与自动化，掌握程度以隔离环境中的部署、故障定位和恢复验证；同时收录本机 WSL 使用中的实际问题。

## 学习路线：从零基础到独立管理服务器

**结论**：按"基础使用 → 单机管理 → 网络服务与安全 → 故障诊断和性能 → 自动化与交付 → 专家方向"推进，每阶段以可复现实验验收。专家要求能跨层定位复杂故障、解释机制和取舍，并在至少一个方向深入；不是背完所有工具，也不是取得某张证书。

```text
基础使用 > 单机管理 > 网络服务与安全 > 故障诊断与性能 > 自动化与交付 > 专家方向
```

路线横向覆盖启动、进程、内存、文件系统、存储、网络、权限、安全、可观测性和容器等主要机制。

零基础的节奏与资源组合：

- 时间：每天约 1 小时，动手时间过半。
- 第 0 天：`wsl --install` 安装适用于 Linux 的 Windows 子系统（Windows Subsystem for Linux，WSL）的 WSL 2 环境。
- 第 1–4 周：命令行基础。Ubuntu 官方命令行教程通读后，精读《The Linux Command Line》（TLCL）第 1–11 章；中文用鸟哥对应章节；练习 OverTheWire Bandit。
- 第 5–8 周：单机系统管理。鸟哥或 LFS101，辅以 21 天的 Linux Upskill Challenge。
- 第 9–12 周：Bash 脚本与工具链。TLCL 脚本部分＋MIT Missing Semester。
- 第 4–6 月：在真实 VPS 上部署、加固并守护一个自有服务。

里程碑：三个月达日常命令行熟练；四至六个月能独立管理一台服务器。时间估计不保证能力，每阶段以动手任务验收。

资源纪律：只选一条主线——一本书、一门课、一个练习场加一台真实环境。备注：linuxjourney.com 已 301 重定向至 labex.io/linuxjourney，后者内容现状未核实，不入主线。

信源：

- [LPI：Linux Essentials 目标（一手）](https://www.lpi.org/our-certifications/exam-010-objectives/)
- [LPI：LPIC-1 目标（一手）](https://www.lpi.org/our-certifications/exam-101-102-objectives/)
- [LPI：LPIC-2 目标（一手）](https://www.lpi.org/our-certifications/exam-201-202-objectives/)
- [LPI：LPIC-3 方向（一手）](https://www.lpi.org/our-certifications/lpic-3-303-overview/)
- [Linux 内核文档（一手）](https://docs.kernel.org/)
- [GNU Bash 手册（一手）](https://www.gnu.org/software/bash/manual/bash.html)
- [Debian 管理员手册（一手）](https://www.debian.org/doc/manuals/debian-handbook/)
- [Ansible 入门（一手）](https://docs.ansible.com/projects/ansible/latest/getting_started/index.html)
- [Kubernetes 概念（一手）](https://kubernetes.io/docs/concepts/)
- [微软 WSL 安装文档（一手）](https://learn.microsoft.com/en-us/windows/wsl/install)
- [Ubuntu 命令行入门教程（一手）](https://ubuntu.com/tutorials/command-line-for-beginners)
- [LFS101 Introduction to Linux（一手）](https://training.linuxfoundation.org/training/introduction-to-linux/)
- [The Linux Command Line 免费版（一手）](https://linuxcommand.org/tlcl.php)
- [鸟哥的 Linux 私房菜（一手）](https://linux.vbird.org/)
- [OverTheWire Bandit（一手）](https://overthewire.org/wargames/bandit/)
- [Linux Upskill Challenge（一手）](https://linuxupskillchallenge.org/)
- [MIT Missing Semester（一手）](https://missing.csail.mit.edu/)

## LVM 合并两块盘供 Docker 使用

**结论**：可以用逻辑卷管理器（Logical Volume Manager，LVM）把两块盘上纳入管理的空间组成跨盘线性逻辑卷，在其文件系统上存放 Docker 数据，以使用分配给该卷的合并容量。

```text
+-------------+  +-------------+
|   系统盘     |  |   数据盘     |
| 纳入 LVM 的  |  | 纳入 LVM 的  |
| 空间（物理卷）|  | 空间（物理卷）|
+------+------+  +------+------+
       |                |
       +-------+--------+
               |  卷组：合并两盘纳入管理的容量
       +-------+--------+
               |  线性逻辑卷：容量相加，不保证均匀写入，无冗余
       +-------+--------+
               |  文件系统 > Docker 数据目录
```

限制与例外：

- 仅创建卷组或挂载数据盘，不会自动合并 Docker 可用容量。
- 线性卷不保证均匀或并行读写，也无冗余；任一盘故障可能使跨盘文件系统不可用。
- 已有非 LVM 系统分区需规划迁移。

替代方案：若只想减轻系统盘占用，可以保持两盘独立并迁移 Docker 存储。注意：使用 containerd 镜像存储时，须分别考虑 Docker 的 data-root 与 containerd 的 root。

信源：

- [Red Hat：LVM 逻辑卷创建与扩容（一手）](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10/html/configuring_and_managing_logical_volumes/basic-logical-volume-management)
- [Linux 内核：dm-linear 映射机制（一手）](https://www.kernel.org/doc/html/latest/admin-guide/device-mapper/linear.html)
- [Red Hat：RAID 与线性存储的容量、性能和冗余（一手）](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10/html/configuring_and_managing_logical_volumes/configuring-raid-logical-volumes)
- [Red Hat：LVM 物理卷初始化（一手）](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10/html/configuring_and_managing_logical_volumes/managing-lvm-physical-volumes)
- [Docker：守护进程存储目录配置（一手）](https://docs.docker.com/engine/daemon/)

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

## Windows 与 WSL 的文件互通

**结论**：不需要同步技术——两侧访问的是同一份存储，即写即见，不是两份拷贝。

```text
+---------------+--------------------------+--------------------------+
|               | NTFS（Windows 盘）        | ext4（WSL 2 内）          |
+---------------+--------------------------+--------------------------+
| Windows 应用  | 同侧直接读写（快）        | 经 \\wsl$ 路径（9P，慢）  |
+---------------+--------------------------+--------------------------+
| Linux 进程    | 经 /mnt/c 挂载（9P，慢）  | 同侧直接读写（快）        |
+---------------+--------------------------+--------------------------+
```

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

## rg 不可用是什么意思

**结论**：`rg` 是文本搜索工具 ripgrep 的命令名。"rg 不可用"表示当前环境找不到或无法运行该命令；搜索没有匹配不表示命令不可用。

四种情况分别判断：

- 找不到命令：例如未安装，或可执行文件所在目录未列入环境变量 `PATH`。Bash 通常报告 `command not found`，退出状态为 127。
- 找到但无法执行：Bash 退出状态为 126，具体原因必须依据实际报错判断。
- 搜索没有匹配：ripgrep 正常完成搜索，退出状态为 1。
- 文件未进入搜索范围：默认忽略规则可能跳过目标文件。

不能把所有非零退出状态视为工具故障。

默认行为：递归搜索目录、遵守忽略规则、跳过隐藏文件和二进制文件。示例：

```bash
rg -n '关键词' 提问记录/
```

实测（2026-11-01）：本次代理 Bash 会话可运行 `rg`，版本 ripgrep 15.2.0。本机可用性只代表该次会话，不代表其他终端、容器或远程环境。

信源：

- [ripgrep 官方说明（一手）](https://github.com/BurntSushi/ripgrep#ripgrep-rg)
- [Bash 命令查找与执行（一手）](https://www.gnu.org/software/bash/manual/html_node/Command-Search-and-Execution.html)
- [ripgrep 手册源文件：退出状态（一手）](https://github.com/BurntSushi/ripgrep/blob/master/crates/core/flags/doc/template.rg.1)
