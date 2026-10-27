<#-- A theme template cannot read the realms: forward to the ns8-home
     realm resource, which redirects to the right page -->
<#assign home = "${baseUrl}realms/master/ns8-home">
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="robots" content="noindex, nofollow">
    <meta http-equiv="refresh" content="0; url=${home}">
    <title>${productName}</title>
</head>
<body>
    <p><a href="${home}">Continue</a></p>
</body>
</html>
