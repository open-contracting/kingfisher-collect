import ocdskingfisher.cli.commands.base
import ocdskingfisher.sources_util


class RunCLICommand(ocdskingfisher.cli.commands.base.CLICommand):
    command = 'run'

    def __init__(self, config=None):
        self.config = config
        self.sources = ocdskingfisher.sources_util.gather_sources()

    def configure_subparser(self, subparser):
        subparser.add_argument("source", help="run one or more sources", nargs="*")
        subparser.add_argument("--all", help="run all sources",	action="store_true")
        subparser.add_argument("--sample", help="Run sample only", action="store_true")
        subparser.add_argument("--dataversion", help="Specify a data version to resume")
        subparser.add_argument("--newversion",
                               help="Forces the creation of a new data version (If you don't specify this or " +
                                    "--dataversion, the latest version will be used. If there are no versions, a new one will be created.)",
                               action="store_true")

        for source_id, source_class in self.sources.items():
            for argument_definition in source_class.argument_definitions:
                subparser.add_argument('--' + argument_definition['name'], help=argument_definition['help'])

    def run_command(self, args):
        run = []

        if args.all and args.source:
            print("You need to either specify a source or use --all flag, not both.")
            quit(-1)

        if args.all:
            for source_id, source_class in self.sources.items():
                run.append({'id': source_id, 'source_class': source_class})
        elif args.source:
            for selected_source in args.source:
                if selected_source in self.sources:
                    run.append({'id': selected_source, 'source_class': self.sources[selected_source]})
                else:
                    print("We can not find a source that you requested! You requested: %s" % selected_source)
                    quit(-1)

        if not run:
            print("You have not specified anything to run! Try listing your sources names or flag --all")
            print("You can run:")
            for source_id, source_info in sorted(self.sources.items()):
                print(" - %s" % source_id)
            quit(-1)

        remove_dir = False
        sample_mode = args.sample
        data_version = args.dataversion
        new_version = args.newversion

        if args.verbose:
            print("We will run: ")
            for sourceInfo in run:
                print(" - %s" % sourceInfo['id'])
            if sample_mode:
                print("Sample mode is on!")
            else:
                print("Sample mode is off.")

        for source_info in run:

            instance = source_info['source_class'](self.config.data_dir,
                                                   remove_dir=remove_dir,
                                                   sample=sample_mode,
                                                   data_version=data_version,
                                                   new_version=new_version
                                                   )
            instance.set_arguments(args)

            if args.verbose:
                print("Now running: %s (Output Dir: %s, Data Version: %s)" % (source_info['id'], instance.output_directory, instance.data_version))


            if args.verbose:
                print(" - gathering ...")
            instance.run_gather()

            if args.verbose:
                print(" - fetching ...")
            instance.run_fetch()
