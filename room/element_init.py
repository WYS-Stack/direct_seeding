def element_exists(d, elementId, use_xpath=False):
    if use_xpath:
        return d.xpath(elementId).exists
    return d(resourceId=elementId).exists


def element_click_exists(d, elementId, use_xpath=False):
    if use_xpath:
        return d.xpath(elementId).cleck_exists()
    else:
        return d(resourceId=elementId).click_exists()


def element_send_keys(d, eId, eValue, use_xpath=False):
    if use_xpath:
        d.xpath(eId).send_keys(eValue)
    else:
        d(resourceId=eId).send_keys(eValue)


def element_wait(d, elementId, use_xpath=False):
    if use_xpath:
        return d.xpath(elementId).wait()
    return d(resourceId=elementId).wait()


def element_wait_gone(d, elementId, use_xpath=False):
    if use_xpath:
        return d.xpath(elementId).wait_gone()
    return d(resourceId=elementId).wait_gone()


def element_set_text(d, eValue):
    d(focused=True).set_text(eValue)


def element_click(d, elementId, use_xpath=False):
    if use_xpath:
        d.xpath(elementId).click()
    else:
        d(resourceId=elementId).click()


def element_get_text(d, elementId, use_xpath=False):
    if use_xpath:
        return d.xpath(elementId).get_text()
    return d(resourceId=elementId).get_text()


def element_description(d, eValue):
    d(description=eValue)


def element_click_text(d, eValue):
    d(text=eValue).click()
