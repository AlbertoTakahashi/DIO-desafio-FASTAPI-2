if __name__ == "__main__":
    import uvicorn
    uvicorn.run('server:app', host='127.0.0.1', port=8000, log_level='info', reload=True)

