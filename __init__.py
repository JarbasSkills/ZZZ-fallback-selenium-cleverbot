from mycroft import FallbackSkill
from time import sleep
from mycroft_jarbas_utils.browser import BrowserControl


class SeleniumCleverbotSkill(FallbackSkill):
    def __init__(self):
        FallbackSkill.__init__(self)
        self.browser = None

    def initialize(self):
        # get a browser control instance,
        # optionally set to auto-start/restart browser
        self.browser = BrowserControl(self.emitter,
                                      timeout=200)  # autostart=False)
        self.register_fallback(self.handle_ask_cleverbot, 85)

    def handle_ask_cleverbot(self, message):
        ask = message.data.get("utterance", "ask me something")

        # restart webbrowser if it is open (optionally)
        # started = browser.start_browser()
        # if not started:
        #    # TODO throw some error
        #    return
        self.browser.reset_elements()
        # get clevebot url
        url = self.browser.get_current_url()
        if "www.cleverbot.com" not in url:
            open = self.browser.open_url("www.cleverbot.com")
            if open is None:
                return False
        # search this element by type and name it "input"
        self.browser.get_element(data="stimulus", name="input", type="name")
        # clear element named input
        # browser.clear_element("input")
        # send text to element named "input"
        self.browser.send_keys_to_element(text=ask, name="input", special=False)
        # send a key_press to element named "input"
        self.browser.send_keys_to_element(text="RETURN", name="input",
                                     special=True)

        # wait until you find element by xpath and name it success
        received = False
        fails = 0
        response = " "
        while response == " ":
            while not received and fails < 5:
                # returns false when element wasnt found
                # this appears only after cleverbot finishes answering
                received = self.browser.get_element(
                    data=".//*[@id='snipTextIcon']", name="success",
                    type="xpath")
                fails += 1

            # sleep a little, sometimes we truncate the answer
            sleep(0.6)
            # find element by xpath, name it "response"
            self.browser.get_element(data=".//*[@id='line1']/span[1]",
                                name="response", type="xpath")
            # get text of the element named "response"
            response = self.browser.get_element_text("response")
        # clean the used elements for this session
        self.browser.reset_elements()
        # optionally close the browser
        # browser.close_browser()
        if response:
            self.speak(response)
            return True
        return False

    def shutdown(self):
        # shutdown the browser to properly remove the messagebus listeners
        self.browser.shutdown()
        self.browser = None
        super(SeleniumCleverbotSkill, self).shutdown()


def create_skill():
    return SeleniumCleverbotSkill()

