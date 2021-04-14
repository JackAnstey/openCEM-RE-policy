"""Module to host initialisers for sets and parameters"""
__author__ = "José Zapata"
__copyright__ = "Copyright 2018, ITP Renewables, Australia"
__credits__ = ["José Zapata", "Dylan McConnell", "Navid Hagdadi"]
__license__ = "GPLv3"
__maintainer__ = "José Zapata"
__email__ = "jose.zapata@itpau.com.au"

import calendar
import datetime
import cemo.const
import holidays

from pyomo.core.base.param import _NotValid


def init_year_correction_factor(model):
    # pylint: disable=unused-argument
    '''Calculate factor to adjust dispatch periods different to 8760 hours'''
    year = datetime.datetime.strptime(model.t.last(),
                                      '%Y-%m-%d %H:%M:%S').year
    hours = 8760
    if calendar.isleap(year):
        hours = 8784
    return hours / len(model.t)


def init_zones_in_regions(model):
    # pylint: disable=unused-argument
    '''Return zones in region tuples for declared regions'''
    for i in cemo.const.ZONES_IN_REGIONS:
        if i[0] in model.regions and i[1] in model.zones:
            yield i


def init_intercons_in_zones(model):
    # pylint: disable=unused-argument
    '''Return zone interconnector pairs for declared zones'''
    for zone_pair in [(zone_source, zone_dest)
                      for zone_source in cemo.const.ZONE_INTERCONS
                      for zone_dest in cemo.const.ZONE_INTERCONS[zone_source]]:
        if zone_pair[0] in model.zones and zone_pair[1] in model.zones:
            yield zone_pair


def init_stor_rt_eff(model, tech):
    # pylint: disable=unused-argument
    '''Default return efficiency for storage techs'''
    return cemo.const.DEFAULT_STOR_PROPS.get(tech).get("rt_eff", 0)


def init_mincap(model, tech):
    # pylint: disable=unused-argument
    '''Default return mincap for unit commitment techs'''
    return cemo.const.GEN_COMMIT.get('mincap').get(tech, 0)


def init_penalty(model, tech):
    # pylint: disable=unused-argument
    '''Default return penalty for unit commitment techs'''
    return cemo.const.GEN_COMMIT.get('penalty').get(tech, 0)


def init_effrate(model, tech):
    # pylint: disable=unused-argument
    '''Default return effrate for unit commitment techs'''
    return cemo.const.GEN_COMMIT.get('effrate').get(tech, 0)


def init_stor_charge_hours(model, tech):
    # pylint: disable=unused-argument
    '''Default charge hours for storage tech'''
    return cemo.const.DEFAULT_STOR_PROPS.get(tech).get("charge_hours", 0)


def init_zone_demand_factors(model, zone, timestamp):
    dt = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    not_holiday = dt.date() not in (
            holidays.AU(prov=cemo.const.ZONE_DEMAND_PCT.get(zone).get('prov')))
    is_peak = 'off peak'
    if dt.weekday() < 5 and 8 <= dt.hour < 20 and not_holiday:
        is_peak = 'peak'
    return cemo.const.ZONE_DEMAND_PCT.get(zone).get(is_peak)


def init_hyb_col_mult(model, tech):
    # pylint: disable=unused-argument
    '''Default collector multiple for hybrid tech'''
    return cemo.const.DEFAULT_HYB_PROPS.get(tech).get('col_mult', 0)


def init_hyb_charge_hours(model, tech):
    # pylint: disable=unused-argument
    '''Default charge hours for hybrid tech'''
    return cemo.const.DEFAULT_HYB_PROPS.get(tech).get("charge_hours", 0)


def init_intercon_loss_factor(model, source, dest):
    # pylint: disable=unused-argument
    '''Initialise interconnector proportioning factors'''
    return cemo.const.ZONE_INTERCONS.get(source).get(dest).get('loss', 0)


def init_default_capex(model, tech):
    # pylint: disable=unused-argument
    '''Initialise capex with default values per technology

       Defaults can catch gaps in data sources in a manner that is
       numerically safer than declaring a very big number'''
    return cemo.const.DEFAULT_CAPEX.get(tech, 9999)


def build_capex(model):
    # pylint: disable=unused-argument
    '''Build capex numbers from regional cost factors and connection costs

       Build cost times regional cost factor plus connection cost'''
    for zone in model.zones:
        for tech in model.gen_tech_per_zone[zone]:
            if model.cost_gen_build[zone, tech]._value is _NotValid:
                model.cost_gen_build[zone, tech] = model.build_cost[tech] * \
                    model.regional_cost_factor[zone, tech]+model.connection_cost[zone, tech]
        for tech in model.stor_tech_per_zone[zone]:
            if model.cost_stor_build[zone, tech]._value is _NotValid:
                model.cost_stor_build[zone, tech] = model.build_cost[tech] * \
                    model.regional_cost_factor[zone, tech]+model.connection_cost[zone, tech]
        for tech in model.hyb_tech_per_zone[zone]:
            if model.cost_hyb_build[zone, tech]._value is _NotValid:
                model.cost_hyb_build[zone, tech] = model.build_cost[tech] * \
                    model.regional_cost_factor[zone, tech]+model.connection_cost[zone, tech]


def init_default_fuel_price(model, zone, tech):
    # pylint: disable=unused-argument
    '''Assign default price across zone and technologies'''
    return cemo.const.DEFAULT_FUEL_PRICE.get(tech, 100.0)


def init_default_heat_rate(model, zone, tech):
    # pylint: disable=unused-argument
    '''Initialise default heat rate for fuel based generators in each zone'''
    return cemo.const.DEFAULT_HEAT_RATE.get(tech, 15.0)


def init_default_fuel_emit_rate(model, tech):
    # pylint: disable=unused-argument
    '''Default fuel emission rate for fuel based generators'''
    return cemo.const.DEFAULT_FUEL_EMIT_RATE.get(tech, 800)


def init_cost_retire(model, tech):
    # pylint: disable=unused-argument
    '''Default retirement/rehabilitation cost in $/MW per technology'''
    return cemo.const.DEFAULT_RETIREMENT_COST.get(tech, 60000.0)


def init_default_lifetime(model, tech):
    # pylint: disable=unused-argument
    '''Default lifetime for technologies'''
    return cemo.const.DEFAULT_TECH_LIFETIME.get(tech, 30.0)


def init_gen_build_limit(model, zone, tech):
    # pylint: disable=unused-argument
    ''' Default build limits per technology and per zone'''
    return cemo.const.DEFAULT_BUILD_LIMIT.get(zone).get(tech, 50000)


def init_fcr(model, tech):
    # pylint: disable=unused-argument
    '''Calculate fixed charge rate for each technology'''
    return model.all_tech_discount_rate / (
        (model.all_tech_discount_rate + 1)**model.all_tech_lifetime[tech]
        - 1) + model.all_tech_discount_rate


def init_intercon_fcr(model):
    # pylint: disable=unused-argument
    '''Calculate fixed charge rate for transmission
    Assumed lifetime: 50 years'''
    return model.all_tech_discount_rate / (
        (model.all_tech_discount_rate + 1)**50
        - 1) + model.all_tech_discount_rate


def init_intercon_cap_initial(model, zone_source, zone_dest):
    # pylint: disable=unused-argument
    '''Initialise initial transmission limits.

    If a template reads values from other data sources, e.g. from a previous year,
    these defaults are overwritten'''
    return cemo.const.ZONE_INTERCONS.get(zone_source).get(zone_dest).get('limit', 0)


def init_intercon_build_cost(model, zone_source, zone_dest):
    # pylint: disable=unused-argument
    '''Initialise build transmission costs $/MW

    If a template reads values from data sources, these defaults are overwritten
    Return the highest of forward and reverse costs specified'''
    forward = cemo.const.ZONE_INTERCONS.get(zone_source).get(zone_dest).get(
        'buildcost', 2500) * cemo.const.ZONE_INTERCONS.get(zone_source).get(
            zone_dest).get('length')
    reverse = cemo.const.ZONE_INTERCONS.get(zone_dest).get(zone_source).get(
        'buildcost', 2500) * cemo.const.ZONE_INTERCONS.get(zone_dest).get(
            zone_source).get('length')
    return max(forward, reverse)


def init_cap_factor(model, zone, tech, time):
    # pylint: disable=unused-argument
    '''Default capacity factor per hour per technology and per zone.

    Note: Defaults to zero means technology does not generate
    Needed to prevent trace based generators to generate at all
    times when their trace fails to load'''
    if cemo.const.GEN_CAP_FACTOR.get(tech) is not None:
        return cemo.const.GEN_CAP_FACTOR.get(tech)
    return 1
