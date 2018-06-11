import voluptuous as vol

import esphomeyaml.config_validation as cv
from esphomeyaml import pins
from esphomeyaml.const import CONF_DUMP, CONF_ID, CONF_PIN, CONF_TOLERANCE, CONF_BUFFER_SIZE, \
    CONF_FILTER, CONF_IDLE
from esphomeyaml.helpers import App, Pvariable, esphomelib_ns, gpio_input_pin_expression, add

remote_ns = esphomelib_ns.namespace('remote')

RemoteReceiverComponent = remote_ns.RemoteReceiverComponent

DUMPERS = {
    'lg': remote_ns.LGDumper,
    'nec': remote_ns.NECDumper,
    'panasonic': remote_ns.PanasonicDumper,
    'raw': remote_ns.RawDumper,
    'sony': remote_ns.SonyDumper,
}

CONFIG_SCHEMA = vol.All(cv.ensure_list, [vol.Schema({
    cv.GenerateID(): cv.declare_variable_id(RemoteReceiverComponent),
    vol.Required(CONF_PIN): pins.gpio_input_pin_schema,
    vol.Optional(CONF_DUMP, default=[]): vol.All(vol.Lower, cv.one_of(*DUMPERS)),
    vol.Optional(CONF_TOLERANCE): vol.All(cv.percentage_int, vol.Range(min=0)),
    vol.Optional(CONF_BUFFER_SIZE): cv.validate_bytes,
    vol.Optional(CONF_FILTER): cv.positive_time_period_microseconds,
    vol.Optional(CONF_IDLE): cv.positive_time_period_microseconds,
})])


def to_code(config):
    for conf in config:
        pin = None
        for pin in gpio_input_pin_expression(conf[CONF_PIN]):
            yield
        rhs = App.make_remote_receiver_component(pin)
        receiver = Pvariable(conf[CONF_ID], rhs)
        for dumper in conf[CONF_DUMP]:
            add(receiver.add_dumper(DUMPERS[dumper].new()))
        if CONF_TOLERANCE in conf:
            add(receiver.set_tolerance(conf[CONF_TOLERANCE]))
        if CONF_BUFFER_SIZE in conf:
            add(receiver.set_buffer_size(conf[CONF_BUFFER_SIZE]))
        if CONF_FILTER in conf:
            add(receiver.set_filter_us(conf[CONF_FILTER]))
        if CONF_IDLE in conf:
            add(receiver.set_idle_us(conf[CONF_IDLE]))


BUILD_FLAGS = '-DUSE_REMOTE_RECEIVER'