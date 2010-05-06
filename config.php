<?php
# ============================================================================
# CONFIGURATION for <path_cacti>/scripts/ss_get_mysql_stats.php
# ============================================================================
# Define MySQL connection constants in config.php.  Arguments explicitly passed
# in from Cacti will override these.  However, if you leave them blank in Cacti
# and set them here, you can make life easier.
#
# For more options see the script itself.
# ============================================================================

$mysql_user = 'mysql';
$mysql_pass = '';
$mysql_port = 3306;

# Whether to use the script server or not
$use_ss    = FALSE;
