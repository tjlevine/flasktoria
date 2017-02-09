task :build do |t|
    sh "docker build --tag flasktoria:latest ."
end

task :run do |t|
    sh "docker run -p 18080:18080 -p 18081:18081 --net flasktoria-net --name flasktoria --rm flasktoria:latest"
end

task :shell do |t|
    sh "docker exec -it flasktoria /bin/bash"
end
