from auth import authenticate

def main():
    service = authenticate()
    results = service.albums().list(pageSize=50).execute()
    albums = results.get('albums', [])
    if not albums:
        print("No albums found.")
    else:
        print("Your albums:")
        for album in albums:
            print(f"Title: {album['title']}\nID: {album['id']}\n")

if __name__ == "__main__":
    main()
