task :build do |t|
    sh "docker build --tag flasktoria:latest ."
end

task :run do |t|
    sh "docker run -v ~/keys/docker-user:/keys/docker-user -p 8080:8080 -p 18081:18081 --name flasktoria --rm flasktoria:latest"
end