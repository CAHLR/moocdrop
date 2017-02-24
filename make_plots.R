library(ggplot2)
library(readr)

multiplot <- function(..., plotlist=NULL, file, cols=1, layout=NULL, heights=NULL) {
  # http://www.cookbook-r.com/Graphs/Multiple_graphs_on_one_page_(ggplot2)/
  library(grid)
  
  # Make a list from the ... arguments and plotlist
  plots <- c(list(...), plotlist)
  
  numPlots = length(plots)
  
  # If layout is NULL, then use 'cols' to determine layout
  if (is.null(layout)) {
    # Make the panel
    # ncol: Number of columns of plots
    # nrow: Number of rows needed, calculated from # of cols
    layout <- matrix(seq(1, cols * ceiling(numPlots/cols)),
                     ncol = cols, nrow = ceiling(numPlots/cols))
  }
  
  if (numPlots==1) {
    print(plots[[1]])
    
  } else {
    # Set up the page
    grid.newpage()
    if (is.null(heights)) {
      pushViewport(viewport(layout = grid.layout(nrow(layout), ncol(layout))))
      
    } else {
      pushViewport(viewport(layout = grid.layout(nrow(layout), ncol(layout), heights=heights)))
    }
    
    # Make each plot, in the correct location
    for (i in 1:numPlots) {
      # Get the i,j matrix positions of the regions that contain this subplot
      matchidx <- as.data.frame(which(layout == i, arr.ind = TRUE))
      
      print(plots[[i]], vp = viewport(layout.pos.row = matchidx$row,
                                      layout.pos.col = matchidx$col))
    }
  }
}


instructor_courses <- read_csv("~/Documents/code/moocdrop/instructor_courses.csv")
all_courses <- read_csv("~/Documents/code/moocdrop/all_courses.csv")
auc_df <- read_csv("~/Documents/code/moocdrop/auc_score_instructor_paced.csv")
auc_ensemble <- read_csv("~/Documents/code/moocdrop/auc_score_ensemble_2.csv")
auc_lstm <- read_csv("~/Documents/code/moocdrop/auc_score_instructor_paced_feature_lstm.csv")
names(instructor_courses)[1] <- "course"
instructor_courses['institution'] <- gsub('[xX].*', '', instructor_courses$course)
combined_df <- merge(auc_df, instructor_courses, by='course')
combined_df$weeks_until_end <- combined_df$weeks - combined_df$week
# weeks until end vs AUC
ggplot(combined_df, aes(x=weeks_until_end, y=auc_score, group=course)) +
  geom_line(color="#c9d9e2") +
  geom_point() + 
  theme_bw() + 
  xlab("Weeks until end of course") + ylab("AUC")  +
  scale_x_reverse() +
  theme(panel.grid.major.x=element_blank(),
        panel.grid.minor.x=element_blank(),
        text=element_text(family="Times New Roman"))
#qplot(weeks_until_end, auc_score, data=combined_df)

combined_ensemble_df <- merge(auc_ensemble, instructor_courses, by='course')
combined_ensemble_df$weeks_until_end <- combined_ensemble_df$weeks - combined_ensemble_df$week
combined_lstm_df <- merge(auc_lstm, instructor_courses, by='course')
combined_lstm_df$weeks_until_end <- combined_lstm_df$weeks - combined_lstm_df$week

# weeks until end vs AUC ensemble
ggplot(combined_ensemble_df, aes(x=weeks_until_end, y=ensemble, group=course, label=course)) +
  geom_line(color="#c9d9e2") +
  # geom_point() + 
  theme_bw() + 
  geom_text(check_overlap = TRUE) +
  xlab("Weeks until end of course") + ylab("AUC")  +
  scale_x_reverse() +
  theme(panel.grid.major.x=element_blank(),
        panel.grid.minor.x=element_blank(),
        text=element_text(family="Times New Roman"))
# weeks vs AUC ensemble
ensemble_course_split <- ggplot(combined_ensemble_df, aes(x=week, y=ensemble, group=course, label=course)) +
  geom_line(color="#c9d9e2") +
  geom_point(size=0.1) +
  theme_bw() + 
  # geom_text(aes(label=ifelse(weeks_until_end < 1, course, ''))) +
  xlab("Weeks") + ylab("Ensemble AUC")  +
  ylim(c(0.4, 1)) +
  theme(panel.grid.major.x=element_blank(),
        panel.grid.minor.x=element_blank(),
        text=element_text(family="Times New Roman")) +
  scale_x_continuous(breaks = seq(0, 10, 2), limits = c(0, 10))
# weeks vs AUC
rep_course_split <- ggplot(combined_df, aes(x=week, y=auc_score, group=course, label=course)) +
  geom_line(color="#c9d9e2") +
  geom_point(size=0.1) +
  theme_bw() + 
  # geom_text(aes(label=ifelse(weeks>10 & weeks_until_end < 10, course, ''))) +
  xlab("Weeks") + ylab("Representation Learning AUC")  +
  ylim(c(0.4, 1)) +
  theme(panel.grid.major.x=element_blank(),
        panel.grid.minor.x=element_blank(),
        text=element_text(family="Times New Roman")) +
  scale_x_continuous(breaks = seq(0, 10, 2), limits = c(0, 10))
# weeks vs AUC for feature LSTM
lstm_course_split <- ggplot(combined_lstm_df, aes(x=week, y=auc_score, group=course, label=course)) +
  geom_line(color="#c9d9e2") +
  geom_point(size=0.1) +
  theme_bw() + 
  # geom_text(check_overlap = TRUE) +
  xlab("Weeks") + ylab("LSTM AUC")  +
  ylim(c(0.4, 1)) +
  theme(panel.grid.major.x=element_blank(),
        panel.grid.minor.x=element_blank(),
        text=element_text(family="Times New Roman")) +
  scale_x_continuous(breaks = seq(0, 10, 2), limits = c(0, 10))
png("~/Downloads/course_split_plot.png", width = 2000, height = 800, res = 300)
multiplot(ensemble_course_split, rep_course_split, lstm_course_split, cols=3)
dev.off()
# number certified
week1_df <- combined_df[combined_df$week == 1, ]
ggplot(week1_df, aes(x=certified, y=auc_score)) +
  geom_point() + 
  theme_bw() + 
  xlab("Number of students certified") + ylab("AUC")  +
  theme(panel.grid.major.x=element_blank(),
        panel.grid.minor.x=element_blank())
#qplot(certified, auc_score, data=combined_df[combined_df$week == 1, ], main="Week 1 students certified vs AUC")

all_courses$instructor_paced <- all_courses[[1]] %in% instructor_courses[[1]]
all_courses$pacing <- ifelse(all_courses$instructor_paced, "Courses Used", "All Courses")
all_courses$week_count <- floor(all_courses$weeks)

cbPalette <- c("#999999", "#56B4E9","#009E73", "#E69F00",  "#F0E442", "#0072B2", "#D55E00", "#CC79A7")

######################################
# Week count
week_count <- ggplot(all_courses, aes(x=week_count, fill=pacing)) +
  geom_histogram(breaks=seq(0, 52, by=2)) +
  labs(x="Number of Weeks in Course", y="Count") + 
  theme_bw() + guides(fill=FALSE) + 
  scale_fill_manual(values=cbPalette) + #guide_legend(title=NULL))
  scale_y_continuous(expand = c(0, 0), limits = c(0, 22)) +
  theme(panel.grid.major=element_blank(),
        panel.grid.minor=element_blank(),
        text=element_text(family="Times New Roman"),
        plot.margin = unit(c(45.5, 5.5, 5.5, 5.5), "points"))

# Certification numbers
cert_count <- ggplot(all_courses, aes(x=certified, fill=pacing)) +
  geom_histogram(breaks=seq(0, 2000, by=50)) +
  labs(x="Students Certified", y="Count") + 
  theme_bw() + guides(fill=guide_legend(title=NULL)) + scale_fill_manual(values=cbPalette) +
  scale_y_continuous(expand = c(0, 0), limits = c(0, 53)) +
  theme(panel.grid.major=element_blank(),
        panel.grid.minor=element_blank(),
        text=element_text(family="Times New Roman"),
        legend.position = 'top')

# Number of deadlines
deadline_count <- ggplot(all_courses, aes(x=deadline_number, fill=pacing)) +
  geom_histogram(breaks=seq(0, 20, by=1)) +
  labs(x="Number of Deadlines", y="Count") + 
  theme_bw() + guides(fill=FALSE) + scale_fill_manual(values=cbPalette) +
  scale_y_continuous(expand = c(0, 0), limits = c(0, 55)) +
  theme(panel.grid.major=element_blank(),
        panel.grid.minor=element_blank(),
        text=element_text(family="Times New Roman"),
        plot.margin = unit(c(45.5, 5.5, 5.5, 5.5), "points"))

png("~/Downloads/course_stat_plot.png", width = 2100, height = 700, res = 300)
multiplot(week_count, cert_count, deadline_count, cols=3)
dev.off()

library(reshape2)
main_result <- read_csv("~/Documents/code/moocdrop/main_data.csv")
names(main_result)[1] <- "week"
flat_result <- melt(main_result, id.vars = "week")
graph_result <- flat_result[!(flat_result$variable %in% c("num_courses", "rep_confidence")),  ]
graph_result$pretty_variable <- "x"
graph_result$pretty_variable[graph_result$variable == "representation_learning"] <- "LSTM (Representation Learning)"
graph_result$pretty_variable[graph_result$variable == "rnn_lstm"] <- "LSTM"
graph_result$pretty_variable[graph_result$variable == "ensemble"] <- "Ensemble"
graph_result$pretty_variable[graph_result$variable == "knn"] <- "k-Nearest Neighbors"
graph_result$pretty_variable[graph_result$variable == "rf"] <- "Random Forest"
graph_result$pretty_variable[graph_result$variable == "svm"] <- "SVM"
graph_result$pretty_variable[graph_result$variable == "lr"] <- "Logistic Regression"
# The big one
main_palette <- c("#56B4E9", "#E69F00", "#009E73", "#0072B2", "#D55E00", "#CC79A7") # "#F0E442", 
main_graph <- ggplot(data=graph_result, 
       aes(x=week, y=value, group=pretty_variable, color=pretty_variable, shape=pretty_variable)) +
  geom_line() +
  geom_point() + 
  theme_bw() + 
  ylim(c(0.75, 0.98)) +
  xlab("Week") + ylab("AUC") + # Set axis labels
  scale_fill_manual(values=cbPalette) +
  theme(legend.position=c(.8, .25)) + 
  scale_color_manual(values = main_palette, name=NULL) + 
  scale_shape(name=NULL) +
  theme(panel.grid.major.x=element_blank(),
        panel.grid.minor.x=element_blank(),
        text=element_text(family="Times New Roman")) +
  scale_x_continuous(breaks = seq(1,  10), minor_breaks = seq(1, 9, 2))
  
# Number of course per week
weekly <- ggplot(data = main_result, aes(x=week, y=num_courses)) + geom_bar(stat="identity", fill="gray") +
  theme_bw() + 
  xlab("Week") + ylab("Number of courses") +  
  scale_x_continuous(breaks = seq(1, 10), minor_breaks = seq(1, 9, 2)) +
  theme(panel.grid.major.x=element_blank(),
        panel.grid.minor.x=element_blank(),
        text=element_text(family="Times New Roman"))
#png("~/Downloads/result_plot.png", width = 800, height = 690)
png("~/Downloads/result_plot.png", width = 2000, height = 2000, res = 300)
multiplot(main_graph, weekly, heights=c(2,1))
dev.off()
# Number of course per week as line plot
ggplot(data = main_result, aes(x=week, y=num_courses)) + geom_line() +
  theme_bw() + 
  xlab("Week") + ylab("Number of courses") +  
  scale_x_continuous(breaks = seq(1, 10), minor_breaks = seq(1, 9, 2)) +
  theme(panel.grid.major.x=element_blank(),
        panel.grid.minor.x=element_blank())
