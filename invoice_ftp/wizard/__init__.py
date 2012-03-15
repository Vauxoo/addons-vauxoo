import release

if release.version < '6':
    import wizard_facturae_ftp_v5
elif release.version >= '6':
    import wizard_facturae_ftp
