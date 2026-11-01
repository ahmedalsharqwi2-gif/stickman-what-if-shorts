from stickman.score import build as original_build
def build(duration,beats,out,profile,impacts=()):
    return original_build(duration,beats,out,'stickman')
