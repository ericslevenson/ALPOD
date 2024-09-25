'''
author: Eric S. Levenson
Description: Reproduce statistical tests in the manuscript "Glacial History
Modifies Permafrost Controls on Lake and Pond Distribution
'''


# Imports
library(readr)
library(ggplot2)
library(ggridges)
library(PMCMRplus)
# Read data
data <- read_csv("Watersheds/hu12_recreate.csv") # csv of ALPOD intersected with HHD watersheds...available in github repository files
#Order permafrost classes
data$pfextent <- factor(data$pfextent, levels = c("Unfrz", "Isol", "Spora", "Discon", "Cont"))
# calculate lake density
data$dens <- (data$lake_count / data$areakm) * 100
# add epsilon to lake fraction
data$lakeFrac <- data$lakeFrac+1e-9
data$lf <- log10(data$lakeFrac+1e-9) #log transform
data <- data[ which(data$gl_Per < .8), ] # remove glaciated watersheds
data$ls <- log10(data$lake_mean)# log transform lake size


## Table S5: Cuzick tests on all watersheds
subset_data <- data[data$pd == 'unglaciated_fine', ]
attach(subset_data)
cuzickTest(lf,pfextent,continuity=TRUE, "two.sided")
#z = 14.727, p-value < 2.2e-16 trend = increase

subset_data <- data[data$pd == 'postglacial_coarse', ]
attach(subset_data)
cuzickTest(lf,pfextent, "two.sided")
#z = -24.177, p-value < 2.2e-16 trend = decrease

subset_data <- data[data$pd == 'unglaciated_coarse', ]
attach(subset_data)
cuzickTest(lf,pfextent, "greater")
#z = -3.5406, p-value = 0.0003992 trend = decrease

subset_data <- data[data$pd == 'postglacial_fine', ]
attach(subset_data)
cuzickTest(lf,pfextent, "two.sided")
# = -0.075593, p-value = 0.9397 no trend

subset_data <- data[data$glacial == 'unglaciated', ]
attach(subset_data)
cuzickTest(lf,pfextent, "greater")
# z = -23.897, p-value < 2.2e-16 trend = 

subset_data <- data[data$glacial == 'postglacial', ]
attach(subset_data)
cuzickTest(lf,pfextent, "two.sided")
# z = 7.3993, p-value = 1.369e-13 trend = 

# Table S6: Cuzick tests for lowlands
sd <- data[data$elv_min < 300,] # subset lowlands
subset_data <- sd[sd$pd == 'unglaciated_coarse', ]
attach(subset_data)
cuzickTest(subset_data$lf,subset_data$pfextent, "greater")
#z = -0.31113, p-value = 0.7557

subset_data <- sd[sd$pd != 'unglaciated_fine', ]
subset_data <- sd[sd$glacial == 'unglaciated', ]

attach(subset_data)
cuzickTest(lake_mean,pfextent, "two.sided")

ggplot(data, aes(y = dens, x = pfextent)) +
  geom_boxplot(fill = "skyblue", color = "darkblue", outlier.color = "red", outlier.shape = 16, outlier.size = 2) +
  facet_wrap(~ texture2)+
  labs(title = "Box Plot of Values by Category", x = "Permafrost Extent", y = "Lake Fraction") +
  theme_minimal() +
  scale_y_log10()+
  scale_x_discrete(limits = c("Unfrz", "Isol", "Spora", "Discon", "Cont")) +
  theme(plot.title = element_text(hjust = 0.5))

ggplot(sd, aes(x = lakeFrac, y=pfextent)) +
  geom_density_ridges(scale=2)
len(data)

## ***LAKE SIZE***
# Table S7: Cuzick tests on all watersheds
subset_data <- data[data$pd == 'unglaciated_fine', ]
attach(subset_data)
cuzickTest(ls,pfextent,continuity=TRUE, "two.sided")
#z = 19.147, p-value < 2.2e-16

subset_data <- data[data$pd == 'unglaciated_coarse', ]
attach(subset_data)
cuzickTest(ls,pfextent,continuity=TRUE, "two.sided")
#z = 6.2313, p-value = 4.625e-10

subset_data <- data[data$pd == 'postglacial_coarse', ]
attach(subset_data)
cuzickTest(ls,pfextent,continuity=TRUE, "two.sided")
#z = -14.083, p-value < 2.2e-16

subset_data <- data[data$glacial == 'postglacial', ]
attach(subset_data)
cuzickTest(ls,pfextent,continuity=TRUE, "two.sided")
#z = -2.3822, p-value = 0.01721

# Table S7 Continued: lowlands
sd <- data[data$elv_min < 300,] # subset lowlands
s <- sd[sd$pd == 'unglaciated_fine', ]
attach(s)
cuzickTest(ls,pfextent,"two.sided")

s <- sd[sd$pd == 'unglaciated_coarse', ]
attach(s)
cuzickTest(ls,pfextent,"two.sided")

s <- sd[sd$pd == 'postglacial_fine', ]
attach(s)
cuzickTest(ls,pfextent,"two.sided")

s <- sd[sd$pd == 'postglacial_coarse', ]
attach(s)
cuzickTest(ls,pfextent,"two.sided")

## ***LAKE DENSITY***

## Figure 2 p-values
data$density <- log10(data$dens + 1e-9)
# subset coarse and fine watersheds
coarse <- data[data$texture2 == "coarse",]
fine <- data[data$texture2 == "fine",]
coar <- data[data$texture2 == "coarse",]
coarse[is.na(coarse$pfextent),] <- "Unfrz"
cuzickTest(coar$density, coar$pfextent, "two.sided")
