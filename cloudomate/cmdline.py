import subprocess
import sys
from argparse import ArgumentParser

from CaseInsensitiveDict import CaseInsensitiveDict

from cloudomate.hoster.vps.ccihosting import CCIHosting
from cloudomate.hoster.vps.blueangelhost import BlueAngelHost
from cloudomate.hoster.vps.crowncloud import CrownCloud
from cloudomate.hoster.vps.legionbox import LegionBox
from cloudomate.hoster.vps.linevast import LineVast
from cloudomate.hoster.vps.pulseservers import Pulseservers
from cloudomate.hoster.vps.undergroundprivate import UndergroundPrivate
from cloudomate.hoster.vpn.azirevpn import AzireVpn
from cloudomate.util.settings import Settings
from cloudomate.util.fakeuserscraper import UserScraper
from cloudomate.wallet import Wallet
from cloudomate import wallet as wallet_util


import inspect


commands = ["options", "purchase", "list"]
types = ["vps", "vpn"]
providers = CaseInsensitiveDict({
    "vps": CaseInsensitiveDict({
        "blueangelhost": BlueAngelHost,
        "ccihosting": CCIHosting,
        "crowncloud": CrownCloud,
        "legionbox": LegionBox,
        "linevast": LineVast,
        'pulseservers': Pulseservers,
        "underground": UndergroundPrivate,
    }),
    "vpn": CaseInsensitiveDict({
        "azirevpn": AzireVpn,
    })
})


def execute(cmd=sys.argv[1:]):
    parser = ArgumentParser(description="Cloudomate")

    subparsers = parser.add_subparsers(dest="type")
    add_vps_parsers(subparsers)
    add_vpn_parsers(subparsers)
    subparsers.required = True

    args = parser.parse_args(cmd)
    args.func(args)


def add_vpn_parsers(subparsers):
    vpn_parsers = subparsers.add_parser("vpn")
    vpn_parsers.set_defaults(type="vpn")
    vpn_subparsers = vpn_parsers.add_subparsers(dest="command")
    vpn_subparsers.required = True

    add_parser_list(vpn_subparsers, "vpn")
    add_parser_options(vpn_subparsers, "vpn")
    add_parser_purchase(vpn_subparsers, "vpn")
    add_parser_status(vpn_subparsers, "vpn")
    add_parser_info(vpn_subparsers, "vpn")


def add_vps_parsers(subparsers):
    vps_parsers = subparsers.add_parser("vps")
    vps_parsers.set_defaults(type="vps")
    vps_subparsers = vps_parsers.add_subparsers(dest="command")
    vps_subparsers.required = True

    add_parser_list(vps_subparsers, "vps")
    add_parser_options(vps_subparsers, "vps")
    add_parser_purchase(vps_subparsers, "vps")
    add_parser_status(vps_subparsers, "vps")
    add_parser_vps_setrootpw(vps_subparsers)
    add_parser_vps_get_ip(vps_subparsers)
    add_parser_vps_ssh(vps_subparsers)
    add_parser_info(vps_subparsers, "vps")


def add_parser_list(subparsers, provider_type):
    parser_list = subparsers.add_parser("list", help="List %s providers" % provider_type.upper())
    parser_list.set_defaults(func=list_providers)


def add_parser_options(subparsers, provider_type):
    parser_options = subparsers.add_parser("options", help="List %s provider configurations" % provider_type.upper())
    parser_options.add_argument("provider", help="The specified %s provider" % provider_type.upper(),
                                choices=providers[provider_type])
    parser_options.set_defaults(func=options)


def add_parser_purchase(subparsers, provider_type):
    parser_purchase = subparsers.add_parser("purchase", help="Purchase %s" % provider_type.upper())
    parser_purchase.set_defaults(func=purchase)
    parser_purchase.add_argument("provider", help="The specified provider", choices=providers[provider_type])

    if provider_type == 'vps':
        parser_purchase.add_argument("option", help="The %s option number (see options)" % provider_type.upper(),
                                     type=int)

    parser_purchase.add_argument("-c", "--config", help="Set custom config file")
    parser_purchase.add_argument("-f", help="Don't prompt for user confirmation", dest="noconfirm", action="store_true")
    parser_purchase.add_argument("-e", "--email", help="email")
    parser_purchase.add_argument("-fn", "--firstname", help="first name")
    parser_purchase.add_argument("-ln", "--lastname", help="last name")
    parser_purchase.add_argument("-cn", "--companyname", help="company name")
    parser_purchase.add_argument("-pn", "--phonenumber", help="phone number", metavar="phonenumber")
    parser_purchase.add_argument("-pw", "--password", help="password")
    parser_purchase.add_argument("-a", "--address", help="address")
    parser_purchase.add_argument("-ct", "--city", help="city")
    parser_purchase.add_argument("-s", "--state", help="state")
    parser_purchase.add_argument("-cc", "--countrycode", help="country code")
    parser_purchase.add_argument("-z", "--zipcode", help="zipcode")

    if provider_type == 'vps':
        parser_purchase.add_argument("-rp", "--rootpw", help="root password")
        parser_purchase.add_argument("-ns1", "--ns1", help="ns1")
        parser_purchase.add_argument("-ns2", "--ns2", help="ns2")
        parser_purchase.add_argument("--hostname", help="hostname")
    parser_purchase.add_argument("--randomuser", action="store_true", help="Use random user info")


def add_parser_status(subparsers, provider_type):
    parser_status = subparsers.add_parser("status", help="Get the status of the %s services." % provider_type.upper())
    parser_status.add_argument("provider", help="The specified provider", nargs="?", choices=providers[provider_type])
    parser_status.add_argument("-e", "--email", help="The login email address")
    parser_status.add_argument("-pw", "--password", help="The login password")
    parser_status.set_defaults(func=status)


def add_parser_vps_get_ip(subparsers):
    parser_get_ip = subparsers.add_parser("getip", help="Get the IP address of the specified service.")
    parser_get_ip.add_argument("provider", help="The specified provider", nargs="?", choices=providers['vps'])
    parser_get_ip.add_argument("-n", "--number", help="The number of the service get the IP address for")
    parser_get_ip.add_argument("-e", "--email", help="The login email address")
    parser_get_ip.add_argument("-pw", "--password", help="The login password")
    parser_get_ip.set_defaults(func=get_ip)


def add_parser_vps_ssh(subparsers):
    parser_ssh = subparsers.add_parser("ssh", help="SSH into an active service.")
    parser_ssh.add_argument("provider", help="The specified provider", nargs="?", choices=providers['vps'])
    parser_ssh.add_argument("-n", "--number", help="The number of the service to SSH into")
    parser_ssh.add_argument("-e", "--email", help="The login email address")
    parser_ssh.add_argument("-pw", "--password", help="The login password")
    parser_ssh.add_argument("-p", "--rootpw", help="The root password used to login")
    parser_ssh.add_argument("-u", "--user", help="The user password used to login", default="root")
    parser_ssh.set_defaults(func=ssh)


def add_parser_info(subparsers, provider_type):
    parser_info = subparsers.add_parser("info",
                                        help="Get information of the specified %s service." % provider_type.upper())
    parser_info.add_argument("provider", help="The specified provider", nargs="?", choices=providers[provider_type])
    parser_info.add_argument("-n", "--number",
                             help="The number of the %s service to change the password for" % provider_type.upper())
    parser_info.add_argument("-e", "--email", help="The login email address")
    parser_info.add_argument("-pw", "--password", help="The login password")
    parser_info.set_defaults(func=info)


def add_parser_vps_setrootpw(subparsers):
    parser_setrootpw = subparsers.add_parser("setrootpw", help="Set the root password of the last activated service.")
    parser_setrootpw.add_argument("provider", help="The specified provider", choices=providers['vps'])
    parser_setrootpw.add_argument("-n", "--number", help="The number of the VPS service to change the password for")
    parser_setrootpw.add_argument("-e", "--email", help="The login email address")
    parser_setrootpw.add_argument("-pw", "--password", help="The login password")
    parser_setrootpw.add_argument("-p", "--rootpw", help="The new root password", required=True)
    parser_setrootpw.set_defaults(func=set_rootpw)


def set_rootpw(args):
    provider = _get_provider(args)
    user_settings = _get_user_settings(args, provider.name)
    provider.set_rootpw(user_settings)


def get_ip(args):
    provider = _get_provider(args)
    user_settings = _get_user_settings(args, provider.name)
    ip = provider.get_ip(user_settings)
    print(ip)


def info(args):
    provider = _get_provider(args)
    name, _ = provider.get_metadata()
    user_settings = _get_user_settings(args, name)
    print(("Info for " + name))

    p = provider(user_settings)
    c = p.get_configuration()

    if args.type == "vps":
        _print_info_vps(c)
    elif args.type == "vpn":
        _print_info_vpn(c)


def status(args):
    provider = _get_provider(args)
    name, _ = provider.get_metadata()
    print(("Getting status for %s." % name))
    user_settings = _get_user_settings(args, name)
    p = provider(user_settings)
    s = p.get_status()

    if args.type == "vps":
        row = "{:18}" * 5
        print(row.format("Memory used (GB)", "Storage used (GB)", "Bandwidth used", "Online", "Expiration"))
        print(row.format(str(s.memory_used), str(s.storage_used), str(s.bandwidth_used), str(s.online), s.expiration.isoformat()))

    elif args.type == "vpn":
        row = "{:18}" * 2
        print(row.format("Online", "Expiration"))
        print(row.format(str(s.online), s.expiration.isoformat()))


def options(args):
    provider = _get_provider(args)

    if args.type == "vps":
        _options_vps(provider)
    elif args.type == "vpn":
        _options_vpn(provider)


def purchase(args):
    if "provider" not in vars(args):
        sys.exit(2)
    provider = _get_provider(args)
    name, _ = provider.get_metadata()
    user_settings = _get_user_settings(args, name)

    if args.randomuser:
        _merge_random_user_data(user_settings)

    if not _check_provider(provider, user_settings):
        print("Missing option")
        sys.exit(2)

    if args.type == 'vps':
        _purchase_vps(provider, user_settings, args)
    else:
        _purchase_vpn(provider, user_settings, args)


def _check_provider(provider, config):
    return config.verify_options(provider.get_required_settings())


def _merge_random_user_data(user_settings):
    usergenerator = UserScraper()
    randomuser = usergenerator.get_user()
    for section in randomuser.keys():
        for key in randomuser[section].keys():
            user_settings.put(section, key, randomuser[section][key])


def _get_user_settings(args, provider=None):
    user_settings = Settings()
    if 'config' in vars(args):
        user_settings.read_settings(filename=args.config)
    else:
        user_settings.read_settings()
    _merge_arguments(user_settings, provider, vars(args))
    return user_settings


def _merge_arguments(config, provider, args):
    for key in args:
        if args[key] is not None:
            config.put(provider, key, args[key])


def _purchase_vps(provider, user_settings, args):
    vps_option = args.option
    configurations = provider.get_options()
    if not 0 <= vps_option < len(configurations):
        print(('Specified configuration %s is not in range 0-%s' % (vps_option, len(configurations))))
        sys.exit(1)
    vps_option = configurations[vps_option]
    row_format = "{:15}" * 6
    print("Selected configuration:")
    print((row_format.format("Name", "CPU", "RAM", "Storage", "Bandwidth", "Price")))
    bandwidth = "Unlimited" if vps_option.bandwidth == sys.maxsize else vps_option.bandwidth
    print((row_format.format(
        vps_option.name,
        str(vps_option.cores),
        str(vps_option.memory),
        str(vps_option.storage),
        str(bandwidth),
        str(vps_option.price))))

    if args.noconfirm or (user_settings.has_key('client', 'noconfirm') and user_settings.get('client', "noconfirm") == "1"):
        choice = True
    else:
        choice = _confirmation("Purchase this option?", default="no")
    if choice:
        _register_vps(provider, vps_option, user_settings)
    else:
        return False


def _purchase_vpn(provider, user_settings, args):
    print("Selected configuration:")
    options = provider.get_options()
    _print_option_vpn(provider, options[0])

    if args.noconfirm or (user_settings.has_key('client', 'noconfirm') and user_settings.get('client', "noconfirm") == "1"):
        choice = True
    else:
        choice = _confirmation("Purchase this option?", default="no")

    if choice:
        _register_vpn(provider, user_settings, options[0])
    else:
        return False


def _confirmation(message, default="y"):
    valid_options = {"yes": True, "ye": True, "y": True, "no": False, "n": False}
    if default in valid_options and valid_options[default] is True:
        prompt = "Y/n"
    elif default in valid_options and valid_options[default] is False:
        prompt = "y/N"
    else:
        prompt = "y/n"

    while True:
        try:
            choice = input("%s (%s) " % (message, prompt)).lower()
        except EOFError:
            sys.exit(2)
        if default is not None and choice == '':
            return valid_options[default]
        elif choice in valid_options:
            return valid_options[choice]
        print("Please respond with y[es] or n[o]")


def list_providers(args):
    _list_providers(args.type)


def _print_unknown_provider(provider):
    if provider:
        print(("Unknown provider: %s\n" % provider))
    else:
        print("Please specify a provider")


def _print_unknown_provider_type(provider_type):
    if provider_type:
        print(("Unknown provider type: %s\n" % provider_type))
    else:
        print("Please specify a provider type")


def _list_providers(provider_type):
    print("Providers:")
    for provider in providers[provider_type].values():
        name, website = provider.get_metadata()
        print("   {:15}{:30}".format(name, website))


def _list_provider_types():
    print("Provider Types:")
    for provider_type in types:
        print(("   {:15}".format(provider_type)))


def _options_vps(p):
    name, _ = p.get_metadata()
    print(("Options for %s:\n" % name))
    options = p.get_options()

    # Print heading
    row = "{:<5}" + "{:20}" * 8
    print(row.format("#", "Name", "Cores", "Memory (GB)", "Storage (GB)", "Bandwidth", "Connection (Gbit/s)", "Est. Price (mBTC)", "Price (USD)"))

    for i, option in enumerate(options):
        bandwidth = "Unlimited" if option.bandwidth == sys.maxsize else str(option.bandwidth)

        # Calculate the estimated price
        rate = wallet_util.get_rate("USD")
        fee = wallet_util.get_network_fee()
        gateway = p.get_gateway()
        estimate = gateway.estimate_price(option.price * rate) + fee  # BTC
        estimate = round(1000 * estimate, 2)  # mBTC

        # Print everything
        print(row.format(i, option.name, str(option.cores), str(option.memory), str(option.storage), bandwidth, str(option.connection), str(estimate), str(option.price)))


def _options_vpn(provider):
    name, _ = provider.get_metadata()
    print(("Options for %s:\n" % name))
    options = provider.get_options()

    # Print heading
    row = "{:18}" * 6
    print(row.format("Name", "Protocol", "Bandwidth", "Speed", "Est. Price (mBTC)", "Price (USD)"))

    for option in options:
        bandwidth = "Unlimited" if option.bandwidth == sys.maxsize else str(option.bandwidth)
        speed = "Unlimited" if option.speed == sys.maxsize else option.speed

        # Calculate the estimated price
        rate = wallet_util.get_rate("USD")
        fee = wallet_util.get_network_fee()
        gateway = provider.get_gateway()
        estimate = gateway.estimate_price(option.price * rate) + fee  # BTC
        estimate = round(1000 * estimate, 2)  # mBTC

        # Print everything
        print(row.format(option.name, option.protocol, bandwidth, speed, str(estimate), str(option.price)))


def _register_vps(p, vps_option, settings):
    # For now use standard wallet implementation through Electrum
    # If wallet path is defined in config, use that.
    if settings.has_key('client', 'walletpath'):
        wallet = Wallet(wallet_path=settings.get('client', 'walletpath'))
    else:
        wallet = Wallet()

    provider = p(settings)
    provider.purchase(wallet, vps_option)



def _register_vpn(p, settings, option):
    # For now use standard wallet implementation through Electrum
    # If wallet path is defined in config, use that.
    if 'walletpath' in settings.config:
        wallet = Wallet(wallet_path=settings.get('client', 'walletpath'))
    else:
        wallet = Wallet()

    provider = p(settings)
    provider.purchase(wallet, option)


def _get_provider(args):
    provider_type = args.type
    provider = args.provider
    if not provider_type or provider_type not in providers:
        _print_unknown_provider_type(provider_type)
        _list_provider_types()
        sys.exit(2)

    if not provider or provider not in providers[provider_type]:
        _print_unknown_provider(provider)
        _list_providers(provider_type)
        sys.exit(2)
    return providers[provider_type][provider]


def ssh(args):
    provider = _get_provider(args)
    user_settings = _get_user_settings(args, provider.name)
    ip = provider.get_ip(user_settings)
    user = user_settings.get('user')
    try:
        subprocess.call(['sshpass', '-p', user_settings.get('rootpw'), 'ssh', '-o', 'StrictHostKeyChecking=no',
                         user + '@' + ip])
    except OSError as e:
        print(e)
        print('Install sshpass to use this command')


def _print_info_vps(info_dict):
    row = "{:18}" * 5
    print(row.format("IP address", "Root password"))
    print(row.format(str(s.ip), str(s.root_password)))


    row_format = "{:<25}{:<30}"
    for key in info_dict:
        print((row_format.format(key, info_dict[key])))


def _print_info_vpn(info):
    credentials = "credentials.conf"
    header = "=" * 20

    ovpn = info.ovpn
    ovpn += "\nauth-user-pass " + credentials

    print("\ncredentials.conf")
    print(header)
    print(info.username)
    print(info.password)
    print("\nsettings.ovpn")
    print(header)
    print(ovpn)
    print(header)    


if __name__ == '__main__':
    execute()
