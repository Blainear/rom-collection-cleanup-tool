1
35
2
2. Install dependencies: `pip install -r requirements.txt`
3
36
4
3. Set up IGDB API credentials (optional but recommended)
5
37
6
•
7
38
8
### IGDB API Setup (Optional)
9

10

11
## License
12

13
This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
14

15
## Contributing
16

17
Contributions are welcome! Feel free to open an issue for bug reports or feature requests, or submit a pull request with improvements.
18

19
39
20
•
21
40
22
1. **Register a Twitch developer application**
23
41
24
- Visit the [Twitch Developers console](https://dev.twitch.tv/console)
25
42
26
- Sign in and create a new application to obtain your **Client ID** and **Client Secret**
27
43
28
- Follow the [IGDB Getting Started guide](https://api-docs.igdb.com/#getting-started) for detailed instructions
29
44
30
2. **Request an access token** using your credentials:
31
45
32
```bash
33
46
34
curl -X POST https://id.twitch.tv/oauth2/token \
35
47
36
-d 'client_id=YOUR_CLIENT_ID' \
37
48
38
-d 'client_secret=YOUR_CLIENT_SECRET' \
39
49
40
-d 'grant_type=client_credentials'
41
50
42
```
43
51