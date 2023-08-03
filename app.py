import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns

st.sidebar.title('Whatsapp Chat Analyzer')

uploaded_file = st.sidebar.file_uploader("Choose a File")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    # file in stream formate - convert file in to string formate
    data = bytes_data.decode('utf-8')
    df = preprocessor.preprocess(data)
    st.title("DataFrame")
    st.dataframe(df)

    # fetch unique user
    users_list = df['users'].unique().tolist()
    users_list.remove('group_notification')
    users_list.sort()
    users_list.insert(0,'Overall')

    selected_user = st.sidebar.selectbox('Show analysis wrt',users_list)

    if st.sidebar.button("Show Analysis"):
        
        num_messages, words, num_media_messages, links = helper.fetch_stats(selected_user,df)
        st.title('Statistics')
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header('Total Messages')
            st.title(num_messages)
        with col2:
            st.header('Total Words')
            st.title(words)
        with col3:
            st.header('Media Shared')
            st.title(num_media_messages)
        with col4:
            st.header('Links Shared')
            st.title(links)

        # Timeline
        st.title('Monthly & Yearly Timeline')
        monthly_totals, yearly_totals, daily_totals = helper.monthly_timeline(selected_user, df)
        col1, col2 = st.columns(2)

        with col1:
            # Plot monthly totals
            st.subheader('Monthly Message Totals')
            fig = plt.figure(figsize=(10, 6))
            ax = fig.add_subplot(111)
            ax.set_facecolor('black')  # Set the background color to black
            ax.bar(monthly_totals['month'], monthly_totals['messages'], color='white')
            ax.set_xlabel('Month')
            ax.set_ylabel('Total Messages')
            ax.set_xticks(monthly_totals['month'])
            plt.tight_layout()
            st.pyplot(fig)

        with col2:
            # Plot yearly totals
            st.subheader('Yearly Message Totals')
            fig2 = plt.figure(figsize=(10, 6))
            ax2 = fig2.add_subplot(111)
            ax2.set_facecolor('black')  # Set the background color to black
            ax2.plot(yearly_totals['year'], yearly_totals['messages'], marker='o', color='white')
            ax2.set_xlabel('Year')
            ax2.set_ylabel('Total Messages')
            plt.tight_layout()
            col2.pyplot(fig2)

        col1, col2 = st.columns(2)
        daily_totals = daily_totals
        with col1:
            # Plot Daily Messages totals
            st.subheader('Daily Message Totals')
            fig1 = plt.figure(figsize=(8, 6))
            ax = fig1.add_subplot(111)
            ax.set_facecolor('black')
            ax.plot(daily_totals['date'], daily_totals['messages'], color='white')
            ax.set_xlabel('Date')
            ax.set_ylabel('Total Messages')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig1)

      
        st.title('Activity Map')
        # Plot monthly Messages totals
        busy_month = helper.monthly_activity_map(selected_user,df)
        busy_day = helper.weekly_activity_map(selected_user,df)
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Most Month Day')
            fig = plt.figure(figsize=(8, 6))
            ax = fig.add_subplot(111)
            ax.set_facecolor('black')
            ax.bar(busy_month.index, busy_month.values, color='white')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
        
        with col2:
            st.subheader('Most Busy Day')
            fig2 = plt.figure(figsize=(8, 6))
            ax2 = fig2.add_subplot(111)  
            ax2.set_facecolor('black')
            ax2.bar(busy_day.index, busy_day.values, color='white')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig2)

        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user,df)
        fig, ax = plt.subplots()
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)


        # finding the busiest user in the group(Group-Level)
        if selected_user == 'Overall':
            st.title('Most Busy Users')
            x, new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots()
            col1, col2 = st.columns(2)
            with col1:
                ax.bar(x.index,x.values,color='red')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            with col2:
                st.dataframe(new_df)
        
        # wordcloud
        st.title('WordCloud')
        df_wc = helper.create_wordcloud(selected_user,df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        # Most common words
        common_words = helper.most_common_words(selected_user, df, 'messages')
        fig, ax = plt.subplots()
        ax.barh(common_words[0], common_words[1], color='white')  
        plt.xticks(rotation='vertical')
        ax.set_facecolor('black')  
        st.title('Most Common Words')
        st.pyplot(fig)

        # Emoji Analysis
        emoji_df = helper.emoji_helper(selected_user,df)
        st.title("Emoji Analysis")

        col1,col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)
        with col2:
            fig, ax = plt.subplots()
            ax.pie(emoji_df[1], labels=emoji_df[0], autopct="%0.2f", 
                   colors=['red', 'lightgrey', 'darkgrey', 'grey'])  
            ax.set_facecolor('black')  
            #st.title('Emoji Distribution')
            st.pyplot(fig)
