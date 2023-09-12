'''
Created on 2023-09-12

@author: wf
'''
import os
from ngwidgets.webserver import NiceGuiWebserver,WebserverConfig
from ngwidgets.local_filepicker import LocalFilePicker
from nicegui import ui

class InputWebserver(NiceGuiWebserver):
    """
    a webserver around a single input file of given filetypes
    """
    
    def __init__(self,config:WebserverConfig=None):
        """
        constructor
        """
        NiceGuiWebserver.__init__(self,config=config)
        self.is_local=False
        self.input=""
        
    def input_changed(self,cargs):
        """
        react on changed input
        """
        self.input=cargs.value
        pass
        
    def read_input(self, input_str: str):
        """Reads the given input and handles any exceptions.

        Args:
            input_str (str): The input string representing a URL or local file.
        """
        try:
            ui.notify(f"reading {input_str}")
            if self.log_view:
                self.log_view.clear()
            self.error_msg = None
        except BaseException as e:
            self.handle_exception(e, self.do_trace)

    async def read_and_optionally_render(self,input_str):
        """Reads the given input and optionally renders the given input

        Args:
            input_str (str): The input string representing a URL or local file.
        """
        self.input_input.set_value(input_str)
        self.read_input(input_str)
        if self.render_on_load:
            await self.render(None)
            
    async def reload_file(self):
        """
        reload the input file
        """
        input_str=self.input
        if os.path.exists(input_str):
            input_str=os.path.abspath(input_str)
        allowed=self.is_local
        if not self.is_local:
            for allowed_url in self.allowed_urls:
                if input_str.startswith(allowed_url):
                    allowed=True
        if not allowed:
            ui.notify("only white listed URLs and Path inputs are allowed")
        else:    
            await self.read_and_optionally_render(self.input)
    
    async def open_file(self) -> None:
        """Opens a Local filer picker dialog and reads the selected input file."""
        if self.is_local:
            pick_list = await LocalFilePicker('~', multiple=False)
            if pick_list and len(pick_list)>0:
                input_file=pick_list[0]
                await self.read_and_optionally_render(input_file)          
    pass

    def setup_menu(self):
        """Adds a link to the project's GitHub page in the web server's menu."""
        version=self.config.version
        with ui.header() as self.header:
            self.link_button("home","/","home")
            self.link_button("settings","/settings","settings")
            self.configure_menu()
            self.link_button("github",version.cm_url,"bug_report")
            self.link_button("chat",version.chat_url,"chat")
            self.link_button("help",version.doc_url,"help")

    async def setup_footer(self):
        self.log_view = ui.log(max_lines=20).classes('w-full h-40')        
        
        await super().setup_footer()        
        if self.args.input:
            #await client.connected()
            await self.read_and_optionally_render(self.args.input)
 
    def settings(self):
        """Generates the settings page with a link to the project's GitHub page."""
        self.setup_menu()
        ui.checkbox('debug with trace', value=True).bind_value(self, "do_trace")
        ui.checkbox('render on load',value=self.render_on_load).bind_value(self,"render_on_load")
        self.setup_footer()
        
    def configure_menu(self):
        """
        overrideable menu configuration
        """
        
    def configure_run(self):
        """
        overrideable configuration
        """
        pass
    
        
    def run(self, args):
        """Runs the UI of the web server.

        Args:
            args (list): The command line arguments.
        """
        self.args=args
        self.input=args.input
        self.is_local=args.local
        self.root_path=os.path.abspath(args.root_path) 
        self.render_on_load=args.render_on_load
        self.configure_run()
        ui.run(title=self.config.version.name, host=args.host, port=args.port, show=args.client,reload=False)