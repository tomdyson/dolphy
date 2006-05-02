# profile dolphy calls
import rundolphy
import hotshot

prof = hotshot.Profile("dolphy.prof")
benchtime, stones = prof.runcall(rundolphy.testIndex)
prof.close()