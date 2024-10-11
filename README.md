R1 (released on Sep 25)
Provide a web-based chat environment where the user can interact with the conversational music recommender system (MusicCRS) - 4 points
The user should be able to add songs to a playlist, remove songs from the playlist, view the playlist, and clear the playlist via natural language instructions or commands via the chat - 4 points
[optional] Provide a way for the user to interact more directly with the playlist, not just via the chat - 2 points
[optional] Provide a way for the user to learn about the functionality of the system - 2 points
Tools that may prove useful:

DialogueKitLinks to an external site. - Python library for building conversational information access systems
ChatWidgetLinks to an external site. - Chat widget built with React that can be embedded into any website
R2 (released on Oct 2)
The user should be able to ask basic questions about albums, songs, and artists. For example, "When was album X released?", "How many albums has artist Y released?", or "Which album features song X?". At least one question should be supported for each category: albums, songs, and artists (i.e., a minimum of three questions). - 6 points
(Note: If this feature is demonstrated before R3 is released, static answers can be used. After R3, answers must be fetched from a database.)
[optional] Add support for additional questions related to albums, songs, or artists – 1 point per question, max 3 points
[optional] Dynamically detect which features the user has not yet utilized during their interaction with the system and introduce these features in a non-intrusive manner - 2 points
[optional] Proactively suggest questions the user can ask about songs they add to the playlist - 2 points
R3 (released on Oct 8)
Create and populate a music database that contains title, artist, album, and year for each song. The database should contain at least 100k songs. Any database backend may be used (including relational, NoSQL, and in-memory databases). The database may be populated from any source that allows for non-commercial use of data. - 6 points
Only songs that can be found in the database can be added to the playlist. Songs may be added by title or by combination of artist and title (e.g., "[artist]: [title]" or "[title] by [artist]") - 2 points
[optional] Have the database contain over 1 million songs - 2 points
[optional] Include other metadata fields in the database (e.g., genre) - 1 point per extra field, max 2 points
Useful sources

You can extract songs from a general-purpose knowledge base, such as DBpedia, by either downloadingLinks to an external site. it (older dumpsLinks to an external site. are also fine to use) or querying the SPARQL endpointLinks to an external site. (there are also Python packages to help with thatLinks to an external site.)
MusicBrainz is a knowledge base dedicated to the music domain that provides downloads in different formatsLinks to an external site.
