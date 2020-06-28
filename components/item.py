class Item:
    def __init__(self, use_function=None, targeting=False, targeting_message=None, targeting_radius=2,  **kwargs):
        self.use_function = use_function
        self.function_kwargs = kwargs
        self.targeting = targeting
        self.targeting_radius = targeting_radius
        self.targeting_message = targeting_message

