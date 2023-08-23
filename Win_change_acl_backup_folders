<#
Autor: Sysoev Andrey
email: asysoev@htsts.ru
#>

#start variables block
$date = Get-Date -Format "dd.MM.yyyy"
$folder = "D:\UserFiles" #forder contents users files
$backupfolder = "E:\Archive" #folder to archives users folders
$tempfile = "E:\Temp\list.txt" #temp list of usernames
$7zip = "C:\Program Files\7-Zip\7z.exe" #7zip file path
$logfile = "E:\Archive\!ArchivateLog.txt" #log file for archivating block
$errordel = "E:\Archive\!error_delete_foders.txt" #list of folders that can`t be deleted automaticaly
$sendfile = "E:\Temp\"+$date+".txt" #temp file for send notification over e-mail
$period = "-365" #numbers of days to save archives
$ChDaysDel = (Get-Date).AddDays($Period) #date older than archives will be deleted
#mail notification variables
$from = "sr-htss-fs-02@htsts.ru"
$sendlist = "htss-monitoring-it@htsts.ru", "azvezdov@k-tech.ru" #указываются e-mail как "user_1@domain.local", "user_2@domain.local"
$subject = "Results of archiving users folders (disk P:\) on sr-htss-fs-02"
$server = "mail.aorti.ru"
$port = "587"
#create acl rules to set if permissions on folder is denied
$BuiltinAdmin = New-Object System.Security.Principal.NTAccount("BUILTIN\Administrators")
$BuiltinAdminFullControlAcl = New-Object System.Security.AccessControl.FileSystemAccessRule($BuiltinAdmin,"FullControl","ContainerInherit, ObjectInherit","None","Allow")
$rtiFSadminsFullControlAcl = New-Object System.Security.AccessControl.FileSystemAccessRule("AORTI\fs-htss-admins","FullControl","ContainerInherit, ObjectInherit","None","Allow")
$rtiFSauditReadAcl = New-Object System.Security.AccessControl.FileSystemAccessRule("AORTI\fs-htss-audit","FullControl","ContainerInherit, ObjectInherit","None","Allow")
$DelAuthUsers = New-Object System.Security.AccessControl.FileSystemAccessRule("NT AUTHORITY\Authenticated Users","ReadData,AppendData,ExecuteFile,Synchronize","Allow")
$acl = get-acl -Path $folder
$acl.SetAccessRule($BuiltinAdminFullControlAcl)
$acl.SetAccessRule($rtiFSadminsFullControlAcl)
$acl.SetAccessRule($rtiFSauditReadAcl)
$acl.RemoveAccessRule($DelAuthUsers)
#end of variables block

#start prepearing file to sending e-mail notification block
"Результаты работы скрипта архивации папок отключенных пользователей и очистки старых архивов диска Р:\" | Out-File -FilePath $sendfile -Append
" " | Out-File -FilePath $sendfile -Append
"Результаты архивирования папок отключенных пользователей:" | Out-File -FilePath $sendfile -Append
" " | Out-File -FilePath $sendfile -Append
#end of  prepearing file to sending e-mail notification block

#start clear temp file block
if (Test-Path -Path $tempfile)
{
    Remove-Item $tempfile -Force -ErrorAction SilentlyContinue
    if (!($?))
    {
    logtext= "!!! Не удалось удалить временный файл "+$tempfile+". Продолжение невозможно."
    $logtext | Out-File -FilePath $logfile -Append
    $logtext | Out-File -FilePath $sendfile -Append
    $body = Get-Content $sendfile | Out-String

    Send-MailMessage -From $from -To $sendlist -Encoding UTF8 -Subject $subject -Body $body -SmtpServer $server -Port $port
    Remove-Item $sendfile -Force
    exit
    }
}
#end of clear temp file block

#start create list of disabled users block
$items = Get-ChildItem -Path $folder
foreach ($item in $items)
{
    $value = Get-ADUser -Identity "$item"
    if ($?) {} else
    { $item.Name | Out-File $tempfile -Append }
    if (!($value.Enabled -eq $true))
    { $item.Name | Out-File $tempfile -Append }
}
#end of create list of disabled users block

#start archivating disabled or deleted users folders block
$date = Get-Date -Format "dd.MM.yyyy HH:mm"
"Процедура архивации начата в "+$date | Out-File -FilePath $sendfile -Append
" " | Out-File -FilePath $sendfile -Append
$items = Get-Content $tempfile
foreach ($item in $items)
{
    $soursefolder = $folder+'\'+$item
    if (Test-Path -Path ($soursefolder+'\*')) #check users folder is not empty
    {
        $backupfilename = $backupfolder+'\'+$item+'.zip'
        if (!(Test-Path -Path $backupfilename)) #check existing backup archive
        {
            & $7zip -mx=9 a $backupfilename $soursefolder
            if ($?)
            {
                Remove-Item $soursefolder -Recurse -Force -ErrorAction SilentlyContinue
                if($?) #remove folder successfully
                    {
                        "Папка пользователя "+$item+" заархивирована и удалена." | Out-File -FilePath $sendfile -Append
                    }
                else
                {
                    "!!! Архив создан, но папку пользователя "+$item+" удалить не удалось." | Out-File -FilePath $sendfile -Append
                    $item | Out-File -FilePath $errordel -Append
                }
            }
            else
            {
                takeown /f $soursefolder /r /D Y
                foreach ($subobject in Get-ChildItem -Path $soursefolder -Recurse) { Set-Acl -Path $subobject.FullName -AclObject $acl }
                & $7zip -mx=9 a $backupfilename $soursefolder
                if ($?)
                {
                    "Архив папки "+$item+" создан только после захвата ownership папки пользователя." | Out-File $sendfile -Append
                    Remove-Item $soursefolder -Recurse -Force -ErrorAction SilentlyContinue
                    if ($?)
                        {
                            "Папка пользователя "+$item+" заархивирована и удалена после захвата ownership." | Out-File -FilePath $sendfile -Append
                        }
                }
                else
                {
                    "!!! Не удается создать архив папки пользователя "+$item+" даже после захвата ownership" | Out-File $sendfile -Append
                    $item | Out-File -FilePath $errordel -Append
                }
            }
        }
        else #archive file already exist - write to log
        {
            "!!! Файл архива пользователя "+$item+" уже существует. Необходима проверка и сопоставление учетных записей. Либо исходная папка пользователя не была удалена при прошлой архивации." | Out-File -FilePath $sendfile -Append
        }
    }
    else #folder is empty
    {
        Remove-Item $soursefolder -Recurse -Force -ErrorAction SilentlyContinue
        if ($?) #remove folder successfully
            {
                "Учетная запись отключена или не существует в AD. Папка пользователя "+$item+" пуста. Архивировать нечего. Папка удалена." | Out-File -FilePath $sendfile -Append
            }
        else
        {
            takeown /f $soursefolder /r /D Y
            foreach ($subobject in Get-ChildItem -Path $soursefolder -Recurse) { Set-Acl -Path $subobject.FullName -AclObject $acl }
            Remove-Item $soursefolder -Recurse -Force -ErrorAction SilentlyContinue
            if ($?)
            {
                "Учетная запись отключена или не существует в AD. Папка пользователя "+$item+" пуста. Архивировать нечего. Папка удалена после захвата ownership." | Out-File -FilePath $sendfile -Append
            }
            else
            {
                "Учетная запись отключена или не существует в AD. Папка пользователя "+$item+" пуста, но удалить ее не получилось." | Out-File -FilePath $sendfile -Append
                $item | Out-File -FilePath $errordel -Append
            }
        }
    }
}
Remove-Item $tempfile -Force #clear temp file
$date = Get-Date -Format "dd.MM.yyyy HH:mm"
"Процедура архивации завешена в "+$date | Out-File -FilePath $sendfile -Append
"__________________________________________________________________" | Out-File -FilePath $sendfile -Append
#end of archivating disabled or deleted users folders block

#start prepearing file to sending e-mail notification block
" " | Out-File -FilePath $sendfile -Append
"Результаты удаления архивов отключенных пользователей старше года:" | Out-File -FilePath $sendfile -Append
" " | Out-File -FilePath $sendfile -Append
#end of prepearing file to sending e-mail notification block

#start deleting old archiver of disabled and deleted users block
$items = Get-ChildItem $backupfolder -Exclude *.txt | Where-Object {$_.CreationTime -LT $ChDaysDel}
if ($items.count -gt 0)
{
    foreach ($item in $items)
    {
        Remove-Item $item.FullName -Force
        if ($?) #remove archive file successfully
        {
            $date = Get-Date -Format "dd.MM.yyyy HH:mm"
            "Архив "+$item+" удален "+$date | Out-File -FilePath $sendfile -Append
            " " | Out-File -FilePath $sendfile -Append
        }
        else
        {
            $date = Get-Date -Format "dd.MM.yyyy HH:mm"
            $date+" Архив "+$item+" удалить не получилось." | Out-File -FilePath $sendfile -Append
            " " | Out-File -FilePath $sendfile -Append
        }
    }
}
#end of deleting old archiver of disabled and deleted users block
Get-Content $sendfile | Out-File -FilePath $logfile -Append #write information to log file

#start sending e-mail notification block
$body = Get-Content $sendfile | Out-String

Send-MailMessage -From $from -To $sendlist -Encoding UTF8 -Subject $subject -Body $body -SmtpServer $server -Port $port
Remove-Item $sendfile -Force
#end of sending e-mail notification block
