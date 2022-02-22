from pstats import Stats
stats = Stats('/tmp/cookadream_profile_stats.out')
stats.sort_stats('file')
stats.print_stats()
