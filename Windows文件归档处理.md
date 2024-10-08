```PowerShell
# ---------------------------------------------------------------------------
# Auth:Qing.Yu
# Mail:1753330141@qq.com
# Ver:V1.1
# Date:2024-06-09
# 1. 定义常量
# 2. 以列表方式返回指定路径下符合筛选条件的子目录
# 3. 在列表的基础上生成处理命令，如压缩至指定路径并删除源文件（-sdel）
# 4. 逐一执行生成的处理命令
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 1. 定义常量
# ---------------------------------------------------------------------------
$folders=(
    'D:\Business_Data\FUnd_Data'
    )                               # 待处理目录
$check_Date='2024-06-30'            # 处理早于该日期的文件
$reg_Date='(\\(202)+\d\d{4}){1}$'    # 匹配日期结尾，后期也可替换其他匹配规则

# ---------------------------------------------------------------------------
# 2. 以列表方式返回指定路径下符合筛选条件的子目录
# 最后修改时间早于$check_Data且目录名包含日期特征$reg_Data
# ---------------------------------------------------------------------------
$items=foreach($folder in $folders){
    Get-ChildItem -Path $folder -Recurse -Directory|
    Where-Object -FilterScript{ $_.LastWriteTime -le $check_Date -and $_.FullName -match $reg_Date}|
    Select-Object FullName
    }
$dirs=foreach($item in $items){$item.FullName}

# ---------------------------------------------------------------------------
# 3. 在列表的基础上生成处理命令，如压缩至指定路径并删除源文件（-sdel）
# ---------------------------------------------------------------------------
# $cmds = foreach ($dir in $dirs){ 'cmd /r "c:\Program Files\7-Zip\7z.exe" a',($dir+'.zip' -replace 'D:\\','D:\Archive\'),$dir,' -sdel' -join ' ' }
$cmds = foreach ($dir in $dirs){ "& 'c:\Program Files\7-Zip\7z.exe'","a",("'" + $dir + ".zip'" -replace "D:\\","D:\Archive\"),("'" + $dir + "'"),"-sdel" -join ' ' }
$cmds|ForEach-Object {$_}

# ---------------------------------------------------------------------------
# 4. 逐一执行生成的处理命令
# ---------------------------------------------------------------------------
foreach ($cmd in $cmds){Invoke-Expression $cmd}
```
