# Java SE

Java 标准版（Java Platform, Standard Edition，Java SE）是 Java 语言、类库与运行时的平台。主线：学习路线、书籍网站、JDK 8→25 演化、类库体系、图形化编程。边界：现行依据为官方文档。

## 学习路线与知识体系

先掌握语言、对象、泛型、异常、集合和常用 API，再学并发、反射、模块与运行时机制。每阶段以可运行程序和机制解释验收。这条路线依据 Java SE 21 规范与官方学习资料整理，不是官方统一课程。"完整"指知识领域完整；类和方法的清单以 API 文档为准。先用普通 `javac`、`java` 和一个小程序理解运行路径，再引入其他工具；换版本时应重新核对 API 与预览状态。

```text
工具与执行
  > 语法、类型和控制流
    > 类、对象和类型设计
      > 泛型、异常和注解
        > 核心类库、集合和 Stream
          > I/O、时间、网络等平台 API
            > 并发和虚拟线程
              > 类加载、反射、模块与打包
                > 按项目深入：安全、桌面、本地互操作
练习（查规范、调试、小项目）-- 贯穿语言、类库、运行机制各阶段
```

| 阶段 | 学习重点 | 完成标志 |
| --- | --- | --- |
| 1．工具与执行 | JDK、源文件、编译、启动、调试和文档 | 能从命令行编译、运行、打包并定位简单错误 |
| 2．语言基础 | 类型、变量、表达式、控制流、数组、方法 | 能独立完成命令行程序并解释转换与参数传递 |
| 3．对象与类型设计 | 类、接口、继承、多态、对象契约、现代类型 | 能建立小型模型并说明封装与组合的选择 |
| 4．类型约束与错误处理 | 泛型、异常、资源关闭、注解 | 能设计类型安全的 API，正确传播异常与关闭资源 |
| 5．核心类库与数据处理 | 字符串、数字、集合、Lambda、Stream | 能选择集合并写出可读的数据处理流程 |
| 6．外部数据与平台 API | 文件、字符集、时间、网络、JDBC 等 | 能可靠读取、转换、传输和持久化数据 |
| 7．并发 | 共享状态、任务执行、取消、虚拟线程 | 能说明线程安全条件，控制任务数量和生命周期 |
| 8．运行机制与组织 | 类加载、反射、模块、字节码、打包 | 能解释程序如何加载与运行，诊断依赖和运行问题 |

**1．工具、编译与执行**。用 `jshell` 试验语句；用集成开发环境（Integrated Development Environment，IDE）的断点、单步、调用栈和变量检查调试。程序路径：`.java` 源文件 → `javac` 编译 → `.class` 字节码 → `java` 启动；掌握 `main` 入口、程序参数、系统属性、环境变量、退出码、包名、目录布局、`import` 与类路径（class path）。用 `jar` 制作 Java 归档文件（Java Archive，JAR）并理解清单文件；用 `javadoc` 生成文档、`javap` 查看字节码；后续再用 `jdeps`、`jlink`、`jpackage`、`jdb`、`jcmd`。

**2．语言基础与类型**。源码结构（标识符、字面量、声明、作用域）；八种基本类型、引用类型、`null`、确定赋值、`final`、局部变量类型推断 `var`；数值提升、宽化与窄化转换、溢出、装箱与拆箱。运算覆盖算术、比较、逻辑、位运算、移位与优先级；控制流覆盖 `if`、`switch` 语句与表达式、`for`、增强 `for`、`while`、`do-while`、`break`、`continue`、`return`、`assert`。数组含一维与多维、数组边界；方法含重载、递归、可变参数。Java 参数传递的是**值**；对象参数传递的是引用值。`String` 不可变，配合 `StringBuilder` 与字符串比较；`char` 是 UTF-16 代码单元，处理完整 Unicode 字符时应认识代码点与代理对。

**3．对象模型与现代语言特性**。类与对象：字段、方法、构造器、初始化顺序、实例与 `static` 成员、`this`、`super`、包和四级访问控制。面向对象：封装、继承、多态、抽象类、接口与默认方法；重载、重写、方法隐藏、动态分派、`final`；组合与继承按适用条件选择。类的形态：静态嵌套类、内部类、局部类、匿名类、枚举（`enum`）；记录类（record）、密封类（sealed）、`instanceof` 模式、`switch` 模式和记录模式。对象契约：对象身份与逻辑相等、`equals`、`hashCode`、`toString`、`Comparable`／`Comparator`；可变性、不可变性与防御性复制。

**4．泛型、异常、资源与注解**。泛型（Generics）覆盖泛型类、接口、方法和构造器；上界、通配符、协变读与逆变写、不变性、类型推断、原始类型、类型擦除、桥接方法、可具体化类型、泛型数组限制、堆污染与泛型可变参数。异常区分受检与非受检；掌握 `try`／`catch`／`finally`、多重捕获、异常链与受抑制异常；资源用 `AutoCloseable` 与 `try-with-resources` 关闭。注解（Annotation）：内置注解、自定义 `@interface`、`@Target`、`@Retention`、`@Repeatable`、`@Inherited` 与源码／类文件／运行时保留策略；注解本身不自动执行逻辑；掌握反射读取与编译期注解处理器。

**5．核心类型、集合与函数式处理**。常用类型：`Object`、`Objects`、包装类、`Math`、`BigInteger`、`BigDecimal`、`UUID`、`Optional`、`Arrays`、`Collections`、`RandomGenerator`、`Base64`；区分数值、文本和对象的比较语义。集合框架（Collections Framework）从 `Iterable`、`Iterator`、`Collection` 到 `List`／`Set`／`Queue`／`Deque`／`Map`，加上 `SortedSet`／`NavigableSet`／`SortedMap`／`NavigableMap` 与 JDK 21 的 `SequencedCollection`／`SequencedSet`／`SequencedMap`；常用实现含 `ArrayList`、`LinkedList`、`ArrayDeque`、`PriorityQueue`、`HashSet`、`LinkedHashSet`、`TreeSet`、`HashMap`、`LinkedHashMap`、`TreeMap`、`EnumSet`、`EnumMap`；按遍历、排序、查找、复杂度与键的相等契约选择；可修改集合、不可修改视图和不可变元素分别判断。函数式处理：函数式接口、`java.util.function`、Lambda、方法引用、变量捕获；Stream 掌握数据源、惰性执行、中间与终止操作、`Collector`、基本类型流、并行流与副作用。

**6．文本、时间、文件与外部系统**。文本覆盖 Unicode 代码点、`Charset` 编解码、正则 `Pattern`／`Matcher`、`Locale`、`ResourceBundle` 与数字日期格式化。日期时间用 `java.time`（`Instant`、`LocalDate`、`ZonedDateTime`、`ZoneId` 等）：区分时间点与本地日期时间，掌握时区规则与 `Duration`／`Period`；旧版 `Date`／`Calendar` 只作互操作。输入/输出（Input/Output，I/O）先掌握 `Path`／`Files` 与目录元数据，再学字节流与字符流、缓冲、`ByteBuffer`、`Channel`、`Selector` 与阻塞／非阻塞 I/O；注意对象序列化的格式兼容性与反序列化风险。网络含 `URI`、`InetAddress`、`Socket`、`ServerSocket`、`DatagramSocket`、`HttpClient`、WebSocket 客户端与传输层安全协议（Transport Layer Security，TLS）的超时与字符集用法。数据库走 Java 数据库连接（Java Database Connectivity，JDBC）：`DataSource`、`Connection`、`PreparedStatement`、`ResultSet`、事务与资源关闭；另有 `java.util.logging` 与 `java.xml` 的 DOM、SAX、StAX、JAXP。

**7．并发与线程模型**。基本语义：`Thread`、`Runnable`、`Callable`、线程状态、启动与结束、`join`、中断、取消、超时；竞态、死锁、活锁和饥饿。正确性：`synchronized`、`volatile`、`wait`／`notify`；按 Java 内存模型（Java Memory Model，JMM）理解可见性、原子性、有序性与 happens-before；安全发布、不可变对象、`final` 字段语义。并发工具：`Lock`／`Condition`、原子类与比较并交换（Compare-and-Set，CAS）、`VarHandle`、`ExecutorService` 与线程池、任务队列和拒绝策略、`Future`、`CompletableFuture`、`ForkJoinPool`、`ConcurrentHashMap` 与并发队列、`Semaphore`、`CountDownLatch`、`ThreadLocal`；深入时再读 `LockSupport`、`AbstractQueuedSynchronizer` 与 `Flow` 的发布订阅和背压。虚拟线程（Virtual Thread）JDK 21 正式提供：掌握任务生命周期、中断、阻塞 I/O、资源上限和线程局部变量的成本；适合大量等待 I/O 的任务，**不能**提高 CPU 密集计算的吞吐能力。

**8．类加载、反射、模块与 JVM 基础**。掌握类加载、链接、初始化、类加载器与类身份；虚拟机栈、堆、垃圾回收的基本职责；规范语义与 HotSpot 实现细节分开学习（GC、JIT 与诊断属 JVM 领域，另行展开）。反射含动态代理、`InvocationHandler`、`MethodHandle` 与模块开放边界。代码组织：Java 平台模块系统（Java Platform Module System，JPMS）的 `requires`、`exports`、`opens`、`uses`、`provides`；`ServiceLoader` 与服务提供者接口（Service Provider Interface，SPI）；用 `jdeps` 查依赖、`jlink` 定制运行时、`jpackage` 打包。

**9．按应用需要深入**。安全与密码：`java.security`、`javax.crypto` 的证书、`KeyStore`、`SecureRandom`、`MessageDigest`、`Mac`、`Signature`、`Cipher`、安全提供者与 TLS；先掌握算法、密钥和参数的协议要求，再查具体 API 契约。桌面与系统集成：`java.desktop` 的 AWT／Swing、JavaBeans、音频、图像、打印与无障碍接口；`java.datatransfer`、Java 管理扩展（Java Management Extensions，JMX）与 `java.management.rmi`、`java.instrument` 代理、`java.naming` 的 JNDI、`java.rmi`、`java.prefs`，按场景选学。其他 Java SE 模块：`java.compiler` 的语言模型与注解处理接口、`java.scripting`、`java.sql.rowset`、`java.transaction.xa`、`java.se` 聚合模块；模块清单以 API 概览为准。本地互操作有 Java 本地接口（Java Native Interface，JNI）和外部函数与内存 API（Foreign Function and Memory API，FFM）；FFM 在 JDK 21 属预览 API，使用前核对版本文档；普通 Java SE 学习可放在最后。

**JDK 21 版本节点**。正式特性：记录模式与 `switch` 模式匹配（21 转正）、顺序集合、虚拟线程；`record`、密封类、文本块、`switch` 表达式在早期版本已转正。预览特性：字符串模板、未命名模式与变量、未命名类和实例 `main` 方法——不要把预览语法当成跨版本稳定基础。

**修正：练习基线选 21 还是 25**（2026-10-15 追问）。

- 旧结论（保留）：JDK 21 是本路线的练习基线（2026-09-23）。
- 新结论：新学习者直接以 **JDK 25** 为练习基线。JDK 25 于 2025-09-16 GA，是当前长期支持（Long-Term Support，LTS）版本；JDK 27 于 2026-09-15 GA 但未被标注为 LTS，按 17→21→25 的两年 LTS 节奏，25 仍是当前 LTS。八个阶段与知识领域不变，只把"按 21 版文档核对"替换为"按 25 版文档核对"。
- JDK 25 已核实增量：转正——模块导入声明（JEP 511）、紧凑源文件与实例 `main` 方法（JEP 512；21 中为预览，25 起可正常使用）、灵活构造器体（JEP 513）、Scoped Values（JEP 506）；仍为预览——结构化并发（JEP 505，第五轮）、原始类型模式匹配（JEP 507，第三轮）、Stable Values（JEP 502），预览特性仍不作稳定基础。VM 层另有紧凑对象头（JEP 519）与 AOT 类加载（JEP 514／515）等性能项，不影响语言学习。
- 教材不换：Core Java 13（Java 21）、On Java（Java 8）等在 25 上直接编译运行；两个 LTS 间语言与平台主体完全一致。

**练习链与总验收**。练习链：命令行小程序 → 带 `record`／接口／泛型的领域模型 → 集合与 Stream 数据汇总 → 带字符集和时区处理的文件工具 → 有超时与取消的并发任务 → JAR／模块打包并用 `javap`、`jdeps` 检查。总验收：能解释类型转换、相等契约、集合选择、泛型边界、异常传播、资源关闭、时间语义、线程安全和类加载；能用官方 API 文档确认未记住的具体行为。

信源（均一手，核实日期 2026-09-23 与 2026-10-15）：[Java SE 21 与 JDK 21 规范目录](https://docs.oracle.com/en/java/javase/21/docs/specs/)、[Java SE 21 API 文档](https://docs.oracle.com/en/java/javase/21/docs/api/index.html)、[JDK 21 工具规范](https://docs.oracle.com/en/java/javase/21/docs/specs/man/index.html)、[Dev.java 学习目录](https://dev.java/learn/)、[Java SE 21 语言特性状态](https://docs.oracle.com/en/java/javase/21/language/java-language-changes-summary.html)、[JDK 25 项目页](https://openjdk.org/projects/jdk/25/)、[JDK 27 项目页](https://openjdk.org/projects/jdk/27/)、[JEP 索引](https://openjdk.org/jeps/0)。

## 经典书籍与学习网站

书籍主线：《Java核心技术》第 13 版（2024，覆盖 Java 21）作系统教程；《On Java 中文版》（2022，基于 Java 8）接替已过时的《Java编程思想》；《Effective Java》第 3 版（2018，覆盖至 Java 9）作最佳实践；《Java并发编程实战》（2006）作并发专项。Java 每半年发版、书按 LTS 更新；选书先比对覆盖版本与练习基线的差距，行为争议以官方文档仲裁。

| 书 | 版本／年份 | 覆盖 Java | 定位与取舍 |
| --- | --- | --- | --- |
| 《Java核心技术》（Core Java）卷 I／II | 第 13 版，2024 | Java 21 | 系统主教程；中文第 13 版截至 2026-10-14 未出版（中文最新为第 12 版 2022-05、Java 17） |
| 《Head First Java》 | 第 3 版，2022 | Java 8–17 | 零基础入门，图解风格；深度不足，作第一本而非唯一一本 |
| 《On Java 中文版》基础卷／进阶卷 | 2022（人民邮电出版社，ISBN 978-7-115-58501-1） | Java 8 | 《Java编程思想》的接替者，重讲"为什么"；Lambda 之后的新语法不在书中 |
| 《Java编程思想》（Thinking in Java） | 第 4 版，2006 | Java 5／6 | 语法层已过时，不建议再作入门；思想性内容已并入 On Java |
| 《Effective Java》 | 第 3 版，2018 | 至 Java 9 | 最佳实践；record、密封类、虚拟线程等新特性需自行取舍，截至 2026-10-14 未见第 4 版官方出版信息 |
| 《Java并发编程实战》（JCIP） | 2006 | Java 5／6 | 并发正确性与 JMM 仍权威；虚拟线程不在书中，需补 dev.java 与 JEP 444 |

**网站清单**：

- [dev.java/learn](https://dev.java/learn/)（一手）：Oracle 官方学习站，按"入门 → 语言 → API → 模块 → JVM"组织。
- [The Java Tutorials](https://docs.oracle.com/javase/tutorial/index.html)（一手）：Sun 时代起积累的经典官方教程，内容冻结在 JDK 8，深度大；概念深读可用，行为按新版文档核对。
- docs.oracle.com（一手）：API、语言规范、JVM 规范、工具规范，行为争议的最终依据。
- [Baeldung](https://baeldung.com)（第三方，二手）：英文实战教程库，Spring 生态内容占比高。
- [Jenkov Java 教程](https://jenkov.com/tutorials/java/index.html)（一手）：简洁参考教程，含 Java 7–25 特性摘要，2026-01 仍在更新。
- [廖雪峰 Java 教程](https://liaoxuefeng.com/books/java/index.html)（一手）：中文零基础免费教程；后半延伸到 JavaEE 与 Spring，超出 Java SE 范围。

**dev.java 与经典 Java Tutorials 的分工**。老教程确实比 dev.java 详细：每页固定声明内容按 JDK 8 编写、部分技术已不可用、更新版指向 dev.java；无"已废弃"横幅，但事实冻结。原因是两代产品：老教程按"trail（学习路径）"组织，从 Sun 时代积累约 20 年，基础部分成书为 The Java Tutorial 第 6 版（Java 8）；dev.java 是 Oracle 约 2022–2023 年上线的重建站，逐主题补齐、覆盖不均——虚拟线程、record、switch 模式、模块、jshell 等新特性只有它讲，集合、并发、泛型等经典主题多数尚浅于老教程。用法：成熟概念深读老教程，但 API 与行为一律按现行版本文档核对；老教程中已死或已移出 JDK 的内容（Applet 与部署、扩展机制 JDK 9 移除、JAXB JDK 11 起移出）直接跳过。

**老教程与《Java核心技术》怎么选**。决策变量不是详细度（两者同为书级篇幅、成体系），而是**版本代际、成本、语言**：

- 默认推荐：《Java核心技术》第 13 版作主线——读英文，或以第 12 版中文配合把练习基线换到 17。理由：整条学习路线挂在 JDK 21（现基线 25），书与基线版本接近，省去逐主题"8 → 21 换算"。老教程作免费的第二参考，在泛型、并发、国际化等主题比书更细时深挖。
- 预算敏感替代：老教程当主线 + dev.java 补新特性 + 新版 API 文档仲裁，也可走通；代价是版本换算成本，且 `var`、`record`、密封类、switch 模式、虚拟线程等 Java 8 之后的系统讲解完全缺失（恰为路线第 3／5／7 阶段核心）。
- 2026-10-15 补：练习基线改为 JDK 25 后，Core Java 13（Java 21）与基线差一个 LTS、增量小，"书作主线"的推荐不变；行为核对改用 25 版官方文档。

信源（核实日期 2026-10-14）：一手——[Core Java 第 13 版付印公告（Horstmann 博客）](https://horstmann.com/unblog/2024-06-22/index.html)、[jcip.net](https://jcip.net)、[TIJ4 官方示例代码仓库](https://github.com/BruceEckel/TIJ4-code)、[Head First Java 第 3 版目录页](https://www.oreilly.com/library/view/head-first-java/9781492091646)、[Core Java 第 13 版电子版收录页](https://learning.oreilly.com/library/view/core-java-volume/9780135371671)；二手（书目信息）——[On Java 中文版基础卷（豆瓣）](https://m.douban.com/book/subject/35751619/reviews)、[《Java核心技术：基础知识》第 12 版中文（百度百科）](https://baike.baidu.com/item/JAVA%E6%A0%B8%E5%BF%83%E6%8A%80%E6%9C%AF%EF%BC%9A%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86/15269293)、[京东第 13 版英文版页](https://www.jd.com/hprm/17134fd314da8236f1a6.html)。

## JDK 8 与 JDK 25 差别有多大

跨 11 年、17 个版本，三层换代：语言写法（`var`、`record`、密封类、模式匹配、文本块、模块导入、实例 `main`）、平台结构与默认行为（模块系统与强封装、移出 EE／CORBA／Nashorn／CMS、UTF-8 默认字符集、标准 HttpClient）、运行时（G1 起步到新一代 GC、虚拟线程、Scoped Values、紧凑对象头与 AOT）。向后兼容成立：8 的代码大多可在 25 编译运行；主体知识结构不变，但 8 基线资料需按 25 翻译语法与默认行为。

```text
2014 JDK 8     Lambda + Stream、默认方法、java.time
2017 JDK 9     模块系统 JPMS、jshell、G1 成为默认 GC
2018 JDK 10-11 var、标准 HttpClient、单文件直接运行、移出 Java EE 与 CORBA
2020 JDK 14-15 switch 表达式、文本块、移除 CMS 与 Nashorn
2021 JDK 16-17 record 与 instanceof 模式、密封类、内部 API 默认强封装
2022 JDK 18    UTF-8 成为默认字符集
2023 JDK 21    虚拟线程、switch 模式与记录模式
2025 JDK 25    Scoped Values、模块导入与实例 main、紧凑对象头与 AOT
```

| 层 | JDK 8（2014） | JDK 25（2025） |
| --- | --- | --- |
| 语言 | Lambda／Stream 刚引入（Project Lambda 是 8 的核心特性） | `var`（10）、switch 表达式（14）、文本块（15）、`record`（16）、`instanceof` 模式（16）、密封类（17）、switch／记录模式（21）、模块导入与实例 `main`（25） |
| 平台与 API | 类路径世界；EE 模块（JAXB 等）内置；平台默认字符集；HttpURLConnection | 模块系统（9，JEP 261）与内部 API 默认强封装（16／17，JEP 396／403）；EE／CORBA 移出（11，JEP 320）；UTF-8 默认字符集（18，JEP 400）；标准 HttpClient（11，JEP 321）；SecurityManager 弃用（17，JEP 411） |
| 运行时 | Parallel GC 默认；永久代刚改为元空间 | G1 默认（9 起，JEP 248）；CMS 移除（14，JEP 363）、Nashorn 移除（15，JEP 372）；虚拟线程（21，JEP 444）；Scoped Values（25，JEP 506）；紧凑对象头（25，JEP 519）与 AOT 缓存（25，JEP 514／515） |
| 工具链 | javac／java／jar | 加 jshell（9，JEP 222）、单文件源码直接运行（11，JEP 330）、jlink（9）与 jpackage（16） |

**8 基线资料的翻译清单**：

1. 语法糖重写：示例用 `var`、`record`、switch 表达式、文本块、instanceof／switch 模式改写，行为不变、表达更短。
2. 默认行为：字符集——8 按平台默认（中文 Windows 即 GBK，读文件经典乱码源），18 起默认 UTF-8；反射访问 JDK 内部 API——17 起默认拒绝。
3. 已移出／移除：JAXB／JAX-WS（11 起独立库）、CORBA（11）、Nashorn（15）、CMS GC（14）——8 资料相关章节作废；SecurityManager（17 起弃用）不再新学。
4. 网络示例：HttpURLConnection 换 HttpClient（11）。
5. 并发补充：Thread-per-request 思路在 21 起可用虚拟线程；ThreadLocal 部分场景可换 Scoped Values（25）。

信源（均一手，核实日期 2026-10-15）：[JDK 8 项目页](https://openjdk.org/projects/jdk8/)、[Java 语言特性演进表](https://docs.oracle.com/en/java/javase/21/language/java-language-changes-summary.html)、[JEP 索引](https://openjdk.org/jeps/0)、[JDK 25 项目页](https://openjdk.org/projects/jdk/25/)。

## JDK 类库体系的宏观概览

以 JDK 25 为基线，公开类库分为两类：Java SE 标准 API（模块名以 `java` 开头）和 JDK 专属 API（模块名以 `jdk` 开头）；前者以 `java.base` 为基础，再由其他模块提供数据库、文档、桌面、管理等能力。理解时先按职责定位，再按"模块 → 包 → 类／接口"查找。下列职责分组是教学归纳，不是官方固定分层。

```text
JDK 公开类库
+-- Java SE 标准 API（java.* 模块）
|   +-- java.base（其余命名模块都依赖它）
|   |     语言与对象（java.lang）、集合与函数式（java.util.*）、
|   |     数值/文本/时间、并发、I/O 与基础网络、安全与密码、
|   |     反射、方法句柄、外部函数与内存、class 文件处理
|   +-- java.net.http            > HttpClient 客户端
|   +-- java.sql / java.sql.rowset > 数据库访问
|   +-- java.naming / java.rmi / java.prefs
|   +-- java.xml / java.xml.crypto
|   +-- java.desktop / java.datatransfer > 桌面与多媒体
|   +-- java.logging / java.management(+rmi) / java.instrument
|   +-- java.compiler / java.scripting
+-- JDK 专属公开 API（jdk.* 模块）
    +-- jdk.compiler / jdk.jshell > 开发工具集成
    +-- jdk.jfr                   > 运行事件录制与消费
    +-- jdk.attach                > 附加目标虚拟机
    +-- jdk.httpserver            > 面向简单用途的服务端 API
```

**模块与包的分工**。示例：`java.base` → `java.util` → `List`／`ArrayList`；`java.logging` → `java.util.logging` → `Logger`。模块声明依赖与对外导出；包提供类型命名和组织。除 `java.base` 自身外，命名模块依赖 `java.base`。

**边界**：`javax.crypto`、`javax.sql`、`javax.swing` 均属于 Java SE，`javax` 不等于第三方或废弃；`jdk.jfr` 是公开 API，`jdk` 不等于内部实现；工具模块可以包含命令行工具实现，命令本身与可调用 API 应分开理解；JDBC 提供标准访问 API 与驱动框架，连接具体数据库通常另加对应驱动。

信源（均一手，核实日期 2026-10-15）：[Java SE 25 与 JDK 25 API 总览](https://docs.oracle.com/en/java/javase/25/docs/api/index.html)、[java.base 模块](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/module-summary.html)、[模块描述与依赖](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/module/ModuleDescriptor.html)、[java.net.http](https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/module-summary.html)、[java.sql 包与驱动框架](https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/package-summary.html)、[java.desktop](https://docs.oracle.com/en/java/javase/25/docs/api/java.desktop/module-summary.html)、[java.compiler](https://docs.oracle.com/en/java/javase/25/docs/api/java.compiler/module-summary.html)、[java.logging](https://docs.oracle.com/en/java/javase/25/docs/api/java.logging/module-summary.html)、[jdk.jfr](https://docs.oracle.com/en/java/javase/25/docs/api/jdk.jfr/module-summary.html)、[jdk.httpserver](https://docs.oracle.com/en/java/javase/25/docs/api/jdk.httpserver/module-summary.html)。

## 图形化编程技术有哪些

按层次分四组：官方工具包 AWT、Swing、JavaFX 三代；第三方桌面工具包；绘制层；游戏方向。选型结论：跨平台一致性选 Swing；现代 UI 与 CSS 布局选 JavaFX；原生观感选 SWT；Kotlin 技术栈选 Compose Multiplatform。

```text
java.desktop (Java SE 标准 API)
+-- AWT (重量级: 委托原生控件, 事件模型)
|    +-- Swing (轻量级: 自绘组件, 建于 AWT 之上)
|    |    +-- FlatLaf (外观增强)
|    +-- Java2D (绘制层: Graphics2D + geom)
|
JavaFX (场景图 + CSS + FXML, JDK 11 起独立 > OpenJFX/Gluon)
SWT (Eclipse, 原生控件)
Compose Multiplatform (JetBrains, Kotlin, 可嵌入 Swing)
游戏/3D: LWJGL (OpenGL/Vulkan 绑定) > libGDX (2D/3D 框架)
```

**AWT（Abstract Window Toolkit）**：`java.awt` 包。重量级组件：每个组件委托操作系统原生控件。提供事件模型、布局、Java2D 绘制等基础设施。

**Swing**：`javax.swing` 包。轻量级组件：纯 Java 绘制，不依赖原生控件，跨平台表现一致。构建在 AWT 之上；外观可插拔（`plaf` 包：Metal、Nimbus、Synth）。AWT 与 Swing 均在 `java.desktop` 模块中（JDK 25 核实），属 Java SE 标准 API。

**JavaFX**：场景图（scene graph）+ CSS + FXML。支持桌面、移动与嵌入式。JavaFX 自 11 起脱离 JDK，不再随 JDK 分发，由 OpenJFX 独立演进（现为 27），经 Maven Central 或 Gluon SDK 获取；许可证为 GPL + 类路径例外，与 OpenJDK 相同。配套工具：Scene Builder（可视化布局）、TestFX（UI 测试）。

**SWT（Standard Widget Toolkit）**：Eclipse Foundation 维护。直接使用操作系统原生 UI 能力，支持 Windows（win32）、macOS（Cocoa）、Linux（GTK）；Maven Central 分发。仍活跃。

**Apache Pivot**：已退役（Apache Attic）。末版 2.0.5（2017-07）。新项目不应选用。

**Compose Multiplatform**：JetBrains 出品，Kotlin 语言，声明式 API（与 Jetpack Compose 同源）。桌面目标（Windows、macOS、Linux）为 Stable；可与 Swing 互操作。

**Java2D**：`java.awt.Graphics2D` 与 `java.awt.geom`。二维绘制 API，属 `java.desktop`。它是绘制层，不是控件工具包。

**LWJGL 3（Lightweight Java Game Library）**：原生图形库绑定（OpenGL、OpenGL ES、Vulkan、GLFW 等）。3.4.0 起支持 FFM API，适配 JDK 25。自定位为底层访问库，不是游戏框架。

**libGDX**：基于 OpenGL (ES) 的 2D/3D 游戏框架。1.14.x（2026-05 发布），社区活跃。同一代码库发布桌面、Android、iOS 与 HTML5。

**FlatLaf**：Swing 现代外观（Look and Feel）。3.x 系列，活跃。被 NetBeans、Ghidra、Burp Suite 等采用。

**选型要点**：

- 必须跨平台一致、零额外依赖：Swing（JDK 自带）。
- 现代 UI、CSS 样式、FXML 分离：JavaFX（另加依赖）。
- 原生观感、Eclipse 生态：SWT。
- Kotlin 技术栈、与 Android 共享代码：Compose Multiplatform。
- 游戏或自绘 3D：LWJGL（要底层）或 libGDX（要框架）。
- 退役项（Apache Pivot）不再考虑。

信源（均一手，核实日期 2026-11-01）：[java.desktop 模块（Java SE 25 API）](https://docs.oracle.com/en/java/javase/25/docs/api/java.desktop/module-summary.html)、[OpenJFX 官网](https://openjfx.io/)、[Eclipse SWT 项目页](https://eclipse.dev/eclipse/swt/)、[Apache Pivot 官网（退役公告）](https://pivot.apache.org/)、[Compose Multiplatform 官网](https://kotlinlang.org/compose-multiplatform/)、[LWJGL 3 仓库](https://github.com/LWJGL/lwjgl3)、[libGDX 官网](https://libgdx.com/)、[FlatLaf 仓库](https://github.com/JFormDesigner/FlatLaf)。
