import os

if __name__ == '__main__':

    profile_on = os.environ.get('COOKADREAM_PROFILE', 'NO').upper() == 'YES'

    def main():
        from cookadream.app import main
        main()

    if profile_on:
        import cProfile
        cProfile.run('main()', '/tmp/cookadream_profile_stats.out')
    else:
        main()
