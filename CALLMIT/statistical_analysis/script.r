library('FSA')

subjects <- c('mubench', 'sockshop', 'teastore')
models <- c('phi3.5', 'gemini')
perf_mets <- c('RES_TIME', 'CPU', 'MEM')
mets <- c('precision', 'recall', 'f1')

for (mod in models) {
  for (pmet in perf_mets) {
for (sub in subjects) {

      if (pmet == "MEM" && sub != "sockshop") {
        next  
      }
      for (m in mets) {
        combined_string <- paste(paste('./datasets', paste(sub, mod, pmet, m, sep="_"), sep = '/'), '.csv', sep = '')
        df <- read.csv(combined_string)
        df$group <- as.factor(df$group)
        #perform Kruskal-Wallis Test
        path_res <- paste(paste('./results', paste(sub, mod, pmet, m, sep="_"), sep = '/'), '.txt', sep = '')
        sink(path_res)
        
        result_kT <- kruskal.test(value ~ group, data = df)
        print(result_kT)
        if (is.na(result_kT$p.value) || result_kT$p.value > 0.05) {
          sink()
          next
        }
        
        #perform Dunn's Test with Bonferroni correction for p-values
        result_dT <- dunnTest(value ~ group,
                              data = df,
                              method="bonferroni")
        
        print(result_dT)
        sink()
        
      }
    }
  }
  
  
}
