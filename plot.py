class Plot():
    def __init__(self, json_path):
        self.username = input('plot user (enter username): ') 
        self.dates_axis, self.users = self.load_data(json_path)
        try:
            self.user_interactions = self.users[self.username]
        except:
            print(f"No data for {self.username}")
            exit()

        self.interactions_axis = self.generate_interactions_axis(self.dates_axis, self.user_interactions)


    def load_data(self, json_path):
        import json
        #TODO: validate json path
        with open('data.json') as json_file:
            try:
                data = json.load(json_file)
                return data["dates"], data["users"]
            except:
                print("Failed to get users info. Try --update to crawl the data ")
                exit()


    def generate_interactions_axis(self, dates, interactions):
        return [interactions.count(date) for date in dates ]

    def plot_interactions_over_time(self):
        import matplotlib.pyplot as plt 
        
        fig, ax = plt.subplots(figsize=(10, 10), tight_layout=True)

        plt.xticks(fontsize=8, rotation=90)
        ax.set_yticks(self.interactions_axis)
        ax.plot(self.dates_axis, 
            self.interactions_axis,
            # density = True,  
            # facecolor ='g', 
            ) 

        ax.set_title(f"{self.username}: Interactions over time")
        ax.set_ylabel("Interaction count")
        ax.set_xlabel("Posts date")
        plt.show() 

