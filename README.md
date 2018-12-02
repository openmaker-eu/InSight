# InSight

**InSight** is a platform for analyzing OpenMaker (OM) community and making personalized recommendation.

InSight is alive on https://insight.openmaker.eu.

## InSight Application Programming Interface (API) modules:

In the current improved design of  InSight API, all services are further categorized under four main groups that are detailed below:

* **OM Network Aggregator** <br>
  * Users' CRM and Twitter information is harvested for members who share their accounts and give permission to the OM consortium to do so. <br>

  * Dynamic Data harvested from Twitter (number of followers, shared news) is used to perform community analytics.

* **Profile Analytics**
  * Each user has a self declared skillset and tags when onboarding the system. These skill sets and tags are extensive and are matched with the topics that are used to retrieve and harvest information by the WatchTower. This is the first step in personalized recommendation.
 
  * InSight serves statistical analysis and visualizations of members social network activities. For example, up-to-date visualizations are provided from actual data that shows the changes in the number of a user’s Twitter followers as influenced by the activities such as sharing news. Another example is a dynamic graph showing the follow relationships among the Twitter accounts of the OM community members

  * Performs model based psychrometric analysis of documents for purposes of recommendation, as described in our current publication.

  * Produces community and member-based social network analysis (SNA) metrics, topics, and keywords using friends, followers, and tweets of the OM followers  obtained from Watchtower. For example, a graph showing the follow relationships among the Twitter accounts of the OM community members).

* **Personalized Recommendation**
  * InSight serves news and event recommendations, and matching members in the OM community according to their skillset, tags and psychometric profiles.

  * Psychometric profiling of OM community is performed by asking questions to the users to improve recommendations.

  * User location information is used to recommend relevant for events.

* **Feedback**
  * A mechanism is implemented on the backend (frontend implementation and user UX design pending) with the purpose of the user being able to provide feedback about the quality of recommendations provided by InSight. Various information can be collected and an internal representation can be dynamically updated by assimilating information from users ratings, answers to questions, and actions taken about recommended news and events such as clicking or pagevisits.

You can find a detailed information in the InSight API documentation on https://insight.openmaker.eu/api/v1.1
