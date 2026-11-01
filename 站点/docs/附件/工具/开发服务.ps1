param(
    [ValidateSet('Start', 'Stop', 'Status')]
    [string]$Action = 'Status',

    [ValidateSet('All', 'Infra', 'SqlServer')]
    [string]$Group = 'All'
)

$ErrorActionPreference = 'Stop'

$serviceGroups = @(
    @{
        Name = 'Infra'
        Compose = '/home/luguosong/code-wsl/company/open-cloud-24-10/upda-code/docker-compose/compose.yaml'
        Services = @('mysql', 'redis', 'nacos', 'rabbit-mq', 'qdrant', 'ollama')
        Containers = @('uocs-mysql', 'uocs-redis', 'uocs-nacos', 'uocs-rabbitmq', 'uocs-qdrant', 'uocs-ollama')
    },
    @{
        Name = 'SqlServer'
        Compose = '/home/luguosong/code-wsl/company/old-upda-program/web-service/UPDA.WebService/docker-compose.yml'
        Services = @('mssql')
        Containers = @('updawebservice-mssql-1')
    }
)

foreach ($serviceGroup in $serviceGroups) {
    if ($Group -ne 'All' -and $Group -ne $serviceGroup.Name) {
        continue
    }

    if ($Action -eq 'Start') {
        $dockerArguments = @('compose', '--file', $serviceGroup.Compose, 'start') + $serviceGroup.Services
    } elseif ($Action -eq 'Stop') {
        if ($serviceGroup.Name -eq 'SqlServer') {
            $sqlContainer = $serviceGroup.Containers[0]
            $sqlRunning = & wsl.exe --distribution Ubuntu --exec docker inspect --format '{{.State.Running}}' $sqlContainer
            if ($LASTEXITCODE -ne 0) {
                throw 'Could not inspect the SQL Server container.'
            }
            if (($sqlRunning -join '').Trim() -eq 'true') {
                # This image's PID 1 shell does not forward SIGTERM to SQL Server.
                # Signal only its direct child watchdog; never force-kill the engine.
                & wsl.exe --distribution Ubuntu --exec docker exec $sqlContainer /usr/bin/pkill -TERM -P 1 -x sqlservr
                if ($LASTEXITCODE -notin 0, 1) {
                    throw 'Could not request graceful SQL Server shutdown.'
                }
            }
        }
        # Wait for graceful shutdown. Do not force-kill database processes.
        $dockerArguments = @('stop', '--timeout', '-1') + $serviceGroup.Containers
    } else {
        $statusTemplate = '{{.Name}} | {{.State.Status}} | health={{if .State.Running}}{{if .State.Health}}{{.State.Health.Status}}{{else}}n/a{{end}}{{else}}n/a{{end}} | restart={{.HostConfig.RestartPolicy.Name}}'
        $dockerArguments = @('inspect', '--format', $statusTemplate) + $serviceGroup.Containers
    }

    & wsl.exe --distribution Ubuntu --exec docker @dockerArguments
    if ($LASTEXITCODE -ne 0) {
        throw "Docker $Action failed for $($serviceGroup.Name), exit code $LASTEXITCODE."
    }
}
